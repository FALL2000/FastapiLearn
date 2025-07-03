from pydantic import BaseModel

class ItemSchema(BaseModel):
    title:str
    description:str

    class Config:
        from_attributes = True