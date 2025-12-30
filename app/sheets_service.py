from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from .config import SHEET_ID, CREDS_FILE

# ===========================
# 1. SETUP GOOGLE SHEET
# ===========================
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

sheet = None

def init_sheet():
    global sheet
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        gclient = gspread.authorize(creds)
        sheet = gclient.open_by_key(SHEET_ID).sheet1  # guna sheet pertama
        print("✅ Berjaya sambung ke Google Sheets")
    except gspread.SpreadsheetNotFound as e:
        print("❌ Google Sheet tidak dijumpai atau tiada akses.")
        print("   - Semak GSHEETS_SHEET_ID dalam .env")
        print("   - Pastikan sheet dikongsi dengan client_email dalam credentials.json")
        print("DETAIL:", e)
        sheet = None
    except Exception as e:
        print("❌ Gagal sambung ke Google Sheets (ralat lain):", e)
        sheet = None

# panggil sekali masa import
init_sheet()


def append_state_to_sheet(negeri: str):
    """
    Simpan ke Google Sheet:
    Kolum A = Negeri
    Kolum B = Tarikh (YYYY-MM-DD)
    """
    from .sheets_service import sheet  # pastikan guna global

    if sheet is None:
        raise RuntimeError("Google Sheets tidak tersedia.")

    timestamp = datetime.now().strftime("%Y-%m-%d")
    row = [
        negeri,    # Kolum A
        timestamp  # Kolum B
    ]
    sheet.append_row(row)
