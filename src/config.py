import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class PathConfig(BaseModel):
    input_path: str = "data/input"
    output_path: str = "data/output"
    tempt_path: str = "data/temp"
    
class LLMConfig(BaseModel):
    api_key: str
    model_name: str
    model_id: str

class GlobalConfig:
    GEMINI_CONFIG = LLMConfig(
        api_key=os.environ.get('GOOGLE_API_KEY'),
        model_name="Gemini",
        model_id=os.environ.get('GOOGLE_MODEL')
    )
    PathConfig = PathConfig()
