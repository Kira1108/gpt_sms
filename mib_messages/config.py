from pydantic import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    DB_URI:str = "sqlite:///message_ai.db"
    OPENAI_API_KEY:str = os.getenv("OPENAI_API_KEY",None)
    FEWSHOT_EXAMPLE_PATH = "./example.json"
    
    
@lru_cache()
def get_settings():
    return Settings()