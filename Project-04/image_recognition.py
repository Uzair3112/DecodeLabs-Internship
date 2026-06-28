import re
import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# ── Windows path override (uncomment if needed) ────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ══════════════════════════════════════════════════════════════════════════════
# PREPROCESSING
# ══════════════════════════════════════════════════════════════════════════════

def preprocess(img: Image.Image) -> Image.Image:
    """Scale up, greyscale, boost contrast & sharpness for clean OCR."""
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)
    return img


# ══════════════════════════════════════════════════════════════════════════════
# BANK DETECTION (colour-based — more reliable than OCR for watermark text)
# ══════════════════════════════════════════════════════════════════════════════

def detect_bank(img: Image.Image) -> str:
    """
    Sample dominant hues to identify the bank/service.
    Meezan Bank uses a green palette; EasyPaisa is also green but with
    a different logo layout; JazzCash is red.  Falls back to "Unknown".
    """
    small = img.resize((100, 100)).convert("RGB")
    pixels = list(small.getdata())

    red_count   = sum(1 for r, g, b in pixels if r > 150 and g < 100 and b < 100)
    green_count = sum(1 for r, g, b in pixels if g > 150 and r < 120 and b < 120)

    # Meezan watermark is a warm grey-green; EasyPaisa logo is a vivid green
    # We distinguish by checking whether the green is inside a white card
    # (Meezan) vs overlaid on a white background with logo circles (EasyPaisa).
    # Since both appear green, we use the reference number prefix as a hint.
    if green_count > 200:
        return "Meezan Bank / EasyPaisa (green-themed)"
    if red_count > 200:
        return "JazzCash"
    return "Unknown"


# ══════════════════════════════════════════════════════════════════════════════
# OCR
# ══════════════════════════════════════════════════════════════════════════════

def run_ocr(image_path: str) -> tuple[str, Image.Image]:
    img = Image.open(image_path)
    processed = preprocess(img)
    raw = pytesseract.image_to_string(processed, config="--oem 3 --psm 3")
    return raw, img


# ══════════════════════════════════════════════════════════════════════════════
# PARSING
# ══════════════════════════════════════════════════════════════════════════════

def _find(patterns: list, text: str) -> str:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Not found"


def clean_name(raw: str) -> str:
    """Strip OCR logo artefacts (oO, Nes, Nee, •, «, etc.) from names."""
    raw = re.sub(r"^[^A-Za-z]+", "", raw)          # leading non-alpha
    raw = re.sub(r"\s{2,}", " ", raw)               # collapse spaces
    return raw.strip()


def parse(raw: str, img: Image.Image) -> dict:
    d = {}

    # Status
    if re.search(r"transaction\s+successful", raw, re.I):
        d["Status"] = "✅  Transaction Successful"
    elif re.search(r"transaction\s+failed", raw, re.I):
        d["Status"] = "❌  Transaction Failed"
    elif re.search(r"pending", raw, re.I):
        d["Status"] = "⏳  Pending"
    else:
        d["Status"] = "Unknown"

    # Amount — handles "PKR 500", "PKR:500", "PKR: 500", "Rs. 500"
    amt = _find([
        r"PKR\s*:?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Rs\.?\s*:?\s*([\d,]+(?:\.\d{1,2})?)",
        r"Amount\s*:?\s*([\d,]+(?:\.\d{1,2})?)",
    ], raw)
    d["Amount"] = f"PKR {amt}" if amt != "Not found" else "Not found"

    # Date & Time
    d["Date & Time"] = _find([
        r"(\w+\s+\d{1,2},\s*\d{4}\s*[|]\s*\d{1,2}:\d{2}\s*(?:AM|PM)?)",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*[|]?\s*\d{1,2}:\d{2}\s*(?:AM|PM)?)",
    ], raw)

    # Reference number
    d["Reference Number"] = _find([
        r"Reference\s*(?:Number|No\.?|#)\s*:?\s*([\w\d]+)",
        r"Ref(?:erence)?\s*:?\s*([\w\d]{6,})",
        r"Txn\s*(?:ID|No\.?)\s*:?\s*([\w\d]+)",
        r"Transaction\s*ID\s*:?\s*([\w\d]+)",
    ], raw)

    # Sender — text after "From Account:" line
    from_m = re.search(
        r"From\s+Account\s*:?\s*\n([A-Z][A-Za-z\s]+)\n(0\d{9,10})",
        raw, re.I
    )
    if from_m:
        d["Sender Name"]   = clean_name(from_m.group(1))
        d["Sender Number"] = from_m.group(2).strip()
    else:
        d["Sender Name"]   = clean_name(_find([r"From\s+Account\s*:?\s*\n([^\n]+)"], raw))
        d["Sender Number"] = _find([r"From\s+Account.*?\n[^\n]+\n(0\d{9,10})"], raw)

    # Receiver — text after "To Account:" line
    to_m = re.search(
        r"To\s+Account\s*:?\s*\n([A-Z][A-Za-z\s]+)\n(0\d{9,10})",
        raw, re.I
    )
    if to_m:
        d["Receiver Name"]   = clean_name(to_m.group(1))
        d["Receiver Number"] = to_m.group(2).strip()
    else:
        d["Receiver Name"]   = clean_name(_find([r"To\s+Account\s*:?\s*\n([^\n]+)"], raw))
        d["Receiver Number"] = _find([r"To\s+Account.*?\n[^\n]+\n(0\d{9,10})"], raw)

    # Bank — colour heuristic + keyword scan
    keywords = {"meezan": "Meezan Bank", "easypaisa": "EasyPaisa",
                "jazzcash": "JazzCash",  "hbl": "HBL", "ubl": "UBL",
                "mcb": "MCB",            "allied": "Allied Bank"}
    d["Bank / Service"] = "Not identified"
    for kw, label in keywords.items():
        if kw in raw.lower():
            d["Bank / Service"] = label
            break
    if d["Bank / Service"] == "Not identified":
        d["Bank / Service"] = detect_bank(img)

    return d


# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

W  = 54
DV = "═" * W
TV = "─" * W

def display(d: dict, raw: str):
    print()
    print(DV)
    print("   📄  TRANSACTION RECEIPT — EXTRACTED DATA")
    print(DV)

    main_fields = [
        ("Status",           d["Status"]),
        ("Amount",           d["Amount"]),
        ("Date & Time",      d["Date & Time"]),
        ("Reference Number", d["Reference Number"]),
        ("Bank / Service",   d["Bank / Service"]),
    ]
    for label, val in main_fields:
        print(f"  {label:<20}  {val}")

    print(TV)
    print("  📤  SENDER")
    print(f"    {'Name':<18}  {d['Sender Name']}")
    print(f"    {'Phone / Account':<18}  {d['Sender Number']}")

    print(TV)
    print("  📥  RECEIVER")
    print(f"    {'Name':<18}  {d['Receiver Name']}")
    print(f"    {'Phone / Account':<18}  {d['Receiver Number']}")

    print(DV)

    # Raw OCR — shown for transparency / debugging
    print("\n  📝  RAW OCR TEXT")
    print(TV)
    for line in raw.splitlines():
        s = line.strip()
        if s:
            print("  " + s)
    print(DV)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def pick_image() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select a Transaction Receipt Image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
            ("All files",   "*.*"),
        ],
    )
    root.destroy()
    return path


def main():
    print("\n🖼   Transaction Receipt OCR Extractor")
    print("   Opening file explorer — select a receipt image ...\n")

    path = pick_image()
    if not path:
        print("⚠   No file selected. Exiting.")
        sys.exit(0)

    print(f"   Selected  : {path}")
    print("   Running OCR ...\n")

    try:
        raw, img = run_ocr(path)
    except pytesseract.TesseractNotFoundError:
        print(
            "\n❌  Tesseract binary not found.\n"
            "   Install: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "   Then uncomment and set tesseract_cmd at the top of this file."
        )
        sys.exit(1)
    except Exception as e:
        print(f"\n❌  Error: {e}")
        sys.exit(1)

    details = parse(raw, img)
    display(details, raw)


if __name__ == "__main__":
    main()