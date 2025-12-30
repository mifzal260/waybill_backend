from typing import Optional
import time

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    HTTPException,
    BackgroundTasks,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from .ai_service import process_waybill
from .sheets_service import append_state_to_sheet

app = FastAPI(
    title="Waybill Scanner API",
    description="API waybill, detect negeri ke Google Sheet",
    version="1.0.0",
)

# ===========================
#  CORS
# ===========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
#  ROOT / HEALTHCHECK
# ===========================
@app.get("/")
def root():
    return {"message": "Waybill Scanner API is running"}


# ===========================
#  TEST SPEED (UNTUK DEBUG)
# ===========================
@app.get("/test-speed")
async def test_speed():
    start = time.perf_counter()
    time.sleep(0.1)  # simulate kerja ringan
    duration = time.perf_counter() - start
    return {"ok": True, "server_time": duration}


# ===========================
#  UPLOAD WAYBILL
# ===========================
@app.post("/upload-waybill")
async def upload_waybill(
    background_tasks: BackgroundTasks,               # ❗ TIADA default / Optional
    file: UploadFile = File(...),
    waybill_id: Optional[str] = Form(None),
):
    t0 = time.perf_counter()
    try:
        # 1. Validasi format fail
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Format tidak disokong: {file.content_type!r}",
            )

        # 2. Baca bytes
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Fail kosong atau gagal dibaca.",
            )
        t1 = time.perf_counter()
        print(f"[UPLOAD-WAYBILL] baca fail: {t1 - t0:.2f}s")

        # 3. Proses AI (OCR) dalam threadpool SUPAYA TAK BLOCK event loop
        result = await run_in_threadpool(process_waybill, image_bytes, waybill_id)
        t2 = time.perf_counter()
        print(f"[UPLOAD-WAYBILL] process_waybill: {t2 - t1:.2f}s")

        full_text = result.get("full_text", "")
        negeri = result.get("negeri", "")
        resolved_waybill_id = result.get("waybill_id", "")

        # 4. Jika negeri tidak dikesan → anggap gagal
        if not negeri or negeri.strip() == "":
            print(f"[UPLOAD-WAYBILL] TIADA NEGERI | total: {t2 - t0:.2f}s")
            return {
                "success": False,
                "detail": "Tiada negeri dikesan dari gambar waybill.",
            }

        # 5. Rekod ke Google Sheet DALAM BACKGROUND (tak blokkan response)
        background_tasks.add_task(append_state_to_sheet, negeri)
        t3 = time.perf_counter()
        print(f"[UPLOAD-WAYBILL] schedule GoogleSheet: {t3 - t2:.2f}s")
        print(f"[UPLOAD-WAYBILL] TOTAL server handling: {t3 - t0:.2f}s")

        # 6. Berjaya – TERUS RETURN, tak tunggu Google Sheet siap
        return {
            "success": True,
            "waybill_id": resolved_waybill_id,
            "negeri": negeri,
            "raw_text_preview": full_text[:300],
        }

    except ValueError as e:
        return {
            "success": False,
            "detail": str(e) or "Gagal memproses gambar",
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ralat proses waybill: {e}",
        )
