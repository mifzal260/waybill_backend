from typing import Optional
import re

import easyocr
import numpy as np
import cv2

# ===========================
# 1. SENARAI NEGERI (KEYWORD)
#    HANYA NAMA TEMPAT SEBENAR
# ===========================
NEGERI_KEYWORDS = {
    "Johor": [
        "johor",
        "johor bahru",
        "muar",
        "batu pahat",
        "segamat",
        "kluang",
        "pontian",
        "mersing",
        "pasir gudang",
        "skudai",
        "kulai",
        "ayer hitam",
        "kota tinggi",
        "yong peng",
        "gelang patah",
        "iskandar puteri",
        "nusajaya",
    ],

    "Kedah": [
        "kedah",
        "sungai petani",
        "kuala muda",
        "alor setar",
        "padang terap",
        "kubang pasu",
        "langkawi",
        "jitra",
        "changlun",
        "gurun",
        "baling",
        "kulim",
        "pokok sena",
        "yan",
    ],

    "Kelantan": [
        "kelantan",
        "kota bharu",
        "pasir mas",
        "pasir puteh",
        "tumpat",
        "bachok",
        "machang",
        "kuala krai",
        "gua musang",
        "jeli",
        "rantau panjang",
    ],

    "Melaka": [
        "melaka",
        "malacca",
        "ayer keroh",
        "alor gajah",
        "jasin",
        "masjid tanah",
        "melaka tengah",
    ],

    "Negeri Sembilan": [
        "negeri sembilan",
        "seremban",
        "nilai",
        "port dickson",
        "jelebu",
        "jempol",
        "kuala pilah",
        "rembau",
        "tampin",
    ],

    "Pahang": [
        "pahang",
        "kuantan",
        "temerloh",
        "bentong",
        "pekan",
        "raub",
        "jerantut",
        "kuala lipis",
        "cameron highlands",
        "brinchang",
        "ringlet",
        "genting highlands",
        "rompin",
        "maran",
        "bera",
    ],

    "Perak": [
        "perak",
        "ipoh",
        "taiping",
        "teluk intan",
        "sitiawan",
        "manjung",
        "kuala kangsar",
        "batu gajah",
        "bagan serai",
        "parit buntar",
        "lumut",
        "tapah",
        "kampar",
        "tronoh",
        "air tawar",
    ],

    "Perlis": [
        "perlis",
        "kangar",
        "arau",
        "padang besar",
    ],

    "Pulau Pinang": [
        "pulau pinang",
        "penang",
        "georgetown",
        "gelugor",
        "bukit mertajam",
        "seberang perai",
        "butterworth",
        "nibong tebal",
        "bayan lepas",
        "bayan baru",
        "tanjung bungah",
        "tanjung tokong",
        "permatang pauh",
    ],

    "Sabah": [
        "sabah",
        "kota kinabalu",
        "sandakan",
        "tawau",
        "lahad datu",
        "semporna",
        "kudat",
        "ranau",
        "beaufort",
        "papar",
        "keningau",
        "tenom",
        "putatan",
        "penampang",
        "tuaran",
    ],

    "Sarawak": [
        "sarawak",
        "kuching",
        "miri",
        "sibu",
        "bintulu",
        "limbang",
        "sri aman",
        "sarikei",
        "mukah",
        "betong",
        "serian",
        "kapit",
        "lawas",
    ],

    "Selangor": [
        "selangor",
        "shah alam",
        "klang",
        "sepang",
        "ampang",
        "petaling jaya",
        "subang jaya",
        "puchong",
        "kajang",
        "bangi",
        "cyberjaya",
        "gombak",
        "rawang",
        "batu caves",
        "hulu langat",
        "hulu selangor",
        "kuala selangor",
        "setia alam",
        "meru",
        "serendah",
    ],

    "Terengganu": [
        "terengganu",
        "kuala terengganu",
        "dungun",
        "kemaman",
        "kuala nerus",
        "marang",
        "besut",
        "setiu",
        "hulu terengganu",
    ],

    "WP Kuala Lumpur": [
        "kuala lumpur",
        "cheras",
        "wangsa maju",
        "setapak",
        "kepong",
        "jalan ipoh",
        "jalan kuching",
        "bukit bintang",
    ],

    "WP Putrajaya": [
        "putrajaya",
        "presint",
    ],

    "WP Labuan": [
        "labuan",
    ],
}


def detect_negeri_by_keyword(text: str) -> Optional[str]:
    """
    Cari negeri berdasarkan keyword nama tempat.
    Jika banyak negeri muncul, pilih yang muncul PALING AKHIR.
    Guna word boundary supaya tak match dalam tengah perkataan.
    """
    text_lower = text.lower()

    best_state = None
    best_pos = -1
    best_len = 0

    for negeri, keywords in NEGERI_KEYWORDS.items():
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if not kw_lower:
                continue

            # \b = sempadan perkataan (contoh: space, tanda baca, hujung baris)
            pattern = r"\b" + re.escape(kw_lower) + r"\b"
            matches = list(re.finditer(pattern, text_lower))
            if not matches:
                continue

            # Ambil kemunculan TERAKHIR keyword (alamat penerima biasanya di bawah)
            pos = matches[-1].start()

            if pos > best_pos or (pos == best_pos and len(kw_lower) > best_len):
                best_pos = pos
                best_len = len(kw_lower)
                best_state = negeri

    return best_state


# ===========================
# 2. SETUP EASYOCR
# ===========================
# Model load SEKALI je masa server start
reader = easyocr.Reader(["en"])


def rotate_image(img, angle: int):
    """Rotate image by 0 / 90 / 180 / 270 degrees."""
    if angle == 0:
        return img
    elif angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return img


def decode_and_resize(image_bytes: bytes) -> np.ndarray:
    """
    Decode bytes -> imej dan resize ke saiz maksima
    (supaya kamera 12MP tak terlalu berat).
    """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Gagal decode image")

    h, w = img.shape[:2]

    # Hadkan kepada max_dim px
    MAX_DIM = 1200
    max_hw = max(h, w)
    if max_hw > MAX_DIM:
        scale = MAX_DIM / max_hw
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        h, w = img.shape[:2]

    # Kalau terlalu kecil, besarkan sikit
    if max(h, w) < 600:
        scale = 600 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    return img


def process_waybill(image_bytes: bytes, waybill_id: Optional[str] = None):
    """
    Fungsi utama AI (tanpa poskod):
    - decode & resize imej
    - OCR dengan beberapa rotation (stop awal bila jumpa negeri)
    - detect negeri berdasarkan keyword nama tempat sahaja
    - fallback waybill_id jika tiada
    """
    img = decode_and_resize(image_bytes)

    best_text = ""
    best_angle = 0
    detected_state: Optional[str] = None

    # Cuba rotation; berhenti bila jumpa negeri
    for angle in [0, 90, 180, 270]:
        rotated = rotate_image(img, angle)

        result = reader.readtext(rotated, detail=0, paragraph=True)
        text = " ".join(result).strip()

        print(f"[OCR] angle={angle}°, length={len(text)}")

        if not text:
            continue

        if len(text) > len(best_text):
            best_text = text
            best_angle = angle

        # Cuba detect negeri ikut keyword
        negeri_here = detect_negeri_by_keyword(text)
        if negeri_here:
            detected_state = negeri_here
            best_text = text
            best_angle = angle
            print(f"[OCR] jumpa negeri '{negeri_here}' pada angle {angle}° – stop awal")
            break

    print(f"[OCR] Best angle: {best_angle}°, final length: {len(best_text)}")

    full_text = best_text
    if not full_text.strip():
        raise ValueError("Tiada teks dikesan dari gambar")

    # 1. Cuba keyword nama tempat sahaja
    negeri = detected_state or detect_negeri_by_keyword(full_text)

    # 2. Kalau masih None → UNKNOWN (tak guna poskod langsung)
    if not negeri:
        negeri = "UNKNOWN"

    if waybill_id is None:
        waybill_id = "NO_ID"

    return {
        "full_text": full_text,
        "negeri": negeri,
        "waybill_id": waybill_id,
    }
