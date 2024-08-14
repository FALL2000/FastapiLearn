from functools import wraps
import time
from fastapi import FastAPI, Depends, HTTPException, Request
from models.users import User
from schemas.userSchema import UserSchema
from config.db import Base, engine, sessionLocal
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

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
async def home():
    return {"message": "Hello, World!"}

@app.post("/adduser")
async def add_user(request:UserSchema, db: Session = Depends(get_db)):
    user = User(name=request.name, email=request.email, nickname=request.nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/user/{user_name}")
async def get_users(user_name,db: Session = Depends(get_db)):
    users = db.query(User).filter(User.name == user_name).first()
    return users

@app.get("/user/")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

