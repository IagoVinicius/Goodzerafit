from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):


    class Config:
        case_sensitive = True


settings: Settings = Settings()
