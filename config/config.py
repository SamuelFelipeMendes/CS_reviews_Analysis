from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")
GEMINI_MODEL = "gemini-2.5-flash"
