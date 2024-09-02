# app/config.py
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator, ValidationInfo
from typing import Union, Optional

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DBNAME: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def database_url(cls, v: Optional[str], values: ValidationInfo):
        if isinstance(v, str):
            print("Loading SQLALCHEMY_DATABASE_URI from .docker.env file ...")
            return v
        
        print("Creating SQLALCHEMY_DATABASE_URI from .env file ...")
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get('POSTGRES_USER'),
            password=values.data.get('POSTGRES_PASSWORD'),
            host=values.data.get('POSTGRES_HOST'),
            port=int(values.data.get('POSTGRES_PORT')),
            path=f"{values.data.get('POSTGRES_DBNAME') or ''}",
        ).unicode_string()

    class Config:
        env_file = ".env"

# Create an instance of the settings
settings = Settings()
