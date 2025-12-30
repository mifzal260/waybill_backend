import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

SHEET_ID = os.getenv("GSHEETS_SHEET_ID")
CREDS_FILE = os.getenv("GSHEETS_CREDS_FILE", "credentials.json")

if not SHEET_ID:
    raise RuntimeError("GSHEETS_SHEET_ID tidak ditetapkan dalam .env")

print("DEBUG GSHEETS_SHEET_ID:", SHEET_ID)
print("DEBUG GSHEETS_CREDS_FILE:", CREDS_FILE)
