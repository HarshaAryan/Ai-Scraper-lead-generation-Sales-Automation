from config import settings
import os
from dotenv import load_dotenv

print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

load_dotenv()
print(f"GOOGLE_API_KEY from os after load_dotenv: '{os.environ.get('GOOGLE_API_KEY')}'")
print(f"GOOGLE_API_KEY from settings: '{settings.google_api_key}'")
