# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, field_validator, ValidationInfo
from typing import Union, Optional, List, Dict, Any
from datetime import timedelta

class Settings(BaseSettings):
    # API Information
    API_V1_STR: str = "/api"

    # Database
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

    # Rate limits
    DEFAULT_RATE_LIMIT: str
    DEFAULT_BURST_RATE_LIMIT: str
    DEFAULT_RATE_LIMITS: List[str] = Field(default_factory=list)

    @field_validator("DEFAULT_RATE_LIMITS", mode="before")
    @classmethod
    def default_rate_limits(cls, v: Optional[str], values: ValidationInfo) -> List[str]:
        rate_limit = values.data.get("DEFAULT_RATE_LIMIT")
        burst_rate_limit = values.data.get("DEFAULT_BURST_RATE_LIMIT")
        return [rate_limit, burst_rate_limit]

    # Define cron parameters for request logs cleanup
    REQUEST_CLEANUP_CRON_KWARGS: Dict[str, str] = {
        'minute': '0',
        'hour': '0',        # Runs at midnight
        'day': '*',         # Every day
        'month': '*',       # Every month
        'day_of_week': '*'  # Every day of the week
    }
    REQUEST_CLEANUP_MAX_ROWS: int = 5000000
    
    # Define the age of request logs to be cleaned up
    REQUEST_CLEANUP_AGE: timedelta = timedelta(days=7)

    # Define cron parameters for task logs cleanup
    TASK_CLEANUP_CRON_KWARGS: Dict[str, str] = {
        'minute': '0',
        'hour': '0',        # Runs at midnight
        'day': '1',         # Every first day of the month
        'month': '*',       # Every month
        'day_of_week': '*'  # Every day of the week
    }
    
    # Define the age of task logs to be cleaned up
    TASK_CLEANUP_AGE: timedelta = timedelta(days=30)
    TASK_CLEANUP_MAX_ROWS: int = 5000000

    class Config:
        env_file = ".env"

# Create an instance of the settings
settings = Settings()
