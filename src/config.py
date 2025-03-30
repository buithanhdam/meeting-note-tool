import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Config(BaseModel):
    input_path: str = "data/input"
    output_path: str = "data/output"
    tempt_path: str = "data/temp"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")
    

# Load config
GLOBAL_CONFIG: Config = Config(
    input_path = "data/input",
    output_path = "data/output",
    OPENAI_API_KEY= os.getenv("OPENAI_API_KEY"),
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    )