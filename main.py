from functools import wraps
import subprocess
import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.routing import APIRoute
from models.users import User
from schemas.userSchema import UserSchema
from config.db import Base, engine, sessionLocal
from sqlalchemy.orm import Session
from py3o.template import Template
import os

# Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


"""

def apply_middleware(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if hasattr(func, 'apply_middleware'):  # Vérifie si le décorateur a été appliqué
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Times"] = str(process_time)
            return response
            # print("Middleware appliqué à cette route")
        return await func(request, *args, **kwargs)
    return wrapper
"""

"""
#@app.middleware("http")
async def add_process_time_header(request: Request):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
"""


@app.get("/")
def home():
    return {"message": "Hello, World!"}


@app.post("/adduser")
def add_user(request: UserSchema, db: Session = Depends(get_db)):
    user = User(name=request.name, email=request.email,
                nickname=request.nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/user/{user_name}")
def get_users(user_name, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.name == user_name).first()
    return users


@app.get("/user/")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# Définissez le répertoire de base de votre projet pour des chemins absolus
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Chemin vers votre modèle ODT
template_path = os.path.join(BASE_DIR, "test.odt")

# 2. Chemin de sortie pour le fichier ODT rempli (peut être temporaire si vous ne voulez pas le conserver)
output_odt_path = os.path.join(BASE_DIR, "document_rempli_temp.odt")

# 3. Chemin de sortie pour le fichier PDF (le nom final désiré)
output_pdf_path = os.path.join(BASE_DIR, "document_final.pdf")

# 4. Vos données Python sous forme de dictionnaire
data = {
    "nom_client": "Dupont et Fils",
    "prenom_client": "Fred",
}


@app.get("/generer_pdf_safe", summary="Génère un PDF et le retourne en réponse")
async def generer_pdf_safe():
    try:
        # Vérifiez si le modèle ODT existe
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=500, detail=f"Le fichier modèle ODT n'existe pas : {template_path}"
            )

        # Création du fichier ODT rempli
        template = Template(template_path, output_odt_path)
        template.render(data)
        print(f"Fichier ODT rempli généré : {output_odt_path}")

        # Définissez le chemin où LibreOffice va **temporairement** créer le PDF
        temp_pdf_name = os.path.basename(
            output_odt_path).replace(".odt", ".pdf")
        temp_pdf_path = os.path.join(BASE_DIR, temp_pdf_name)

        # --- Partie cruciale : Utilisation de subprocess.run ---
        # Chemin exact vers soffice.exe
        soffice_path = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"

        # Vérifier si soffice.exe existe
        if not os.path.exists(soffice_path):
            raise HTTPException(
                status_code=500, detail=f"LibreOffice soffice.exe non trouvé à : {soffice_path}. Veuillez vérifier l'installation et le chemin."
            )

        command = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            output_odt_path,  # Pas besoin de guillemets ici, subprocess les gère
            "--outdir", BASE_DIR  # Pas besoin de guillemets ici
        ]

        print(f"Conversion en PDF en cours. Commande: {' '.join(command)}")

        # Exécute la commande
        # capture_output=True et text=True permettent de capturer la sortie (stdout/stderr)
        # check=True lève une exception CalledProcessError si la commande retourne un code d'erreur non nul
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        print("Sortie standard de LibreOffice:", result.stdout)
        print("Erreur standard de LibreOffice:", result.stderr)

        # Vérifie si le fichier PDF temporaire (celui créé par LibreOffice) existe
        if os.path.exists(temp_pdf_path):
            # Renomme le fichier PDF temporaire vers le nom final désiré
            os.rename(temp_pdf_path, output_pdf_path)
            print(f"Fichier PDF généré et renommé : {output_pdf_path}")
        else:
            raise HTTPException(
                status_code=500, detail=f"La conversion PDF a échoué. Le fichier {temp_pdf_path} n'a pas été trouvé. Vérifiez les logs LibreOffice."
            )

        # Retourne le fichier PDF comme réponse
        return FileResponse(
            path=output_pdf_path,
            media_type="application/pdf",
            filename="mon_document.pdf",
        )

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de LibreOffice: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la conversion PDF par LibreOffice: {e.stderr}"
        )
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        raise HTTPException(
            status_code=500, detail=f"Une erreur interne est survenue lors de la génération du PDF : {str(e)}"
        )
