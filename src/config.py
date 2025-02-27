import os
from dotenv import load_dotenv
from pathlib import Path


# Load API key from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set it in the .env file.")
