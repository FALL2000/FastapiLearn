from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str 
    algorithm: str


    class Config:
        env_file = ".env"

            