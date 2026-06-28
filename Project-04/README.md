# 🧾 Transaction Receipt OCR Extractor

A Python script that extracts structured transaction data from mobile banking receipt screenshots using Tesseract OCR and PIL — no API keys, no cloud, runs fully offline.

---

## 📸 Demo

**Input** — any Pakistani mobile banking receipt (EasyPaisa, JazzCash, Meezan Bank, HBL, etc.)

```
════════════════════════════════════════════════════════
   📄  TRANSACTION RECEIPT — EXTRACTED DATA
════════════════════════════════════════════════════════
  Status                ✅  Transaction Successful
  Amount                PKR 500
  Date & Time           May 06, 2026 | 5:38 PM
  Reference Number      0331002345
  Bank / Service        Meezan Bank / EasyPaisa (green-themed)
────────────────────────────────────────────────────────
  📤  SENDER
    Name                HASSAN Tariq
    Phone / Account     032--------
────────────────────────────────────────────────────────
  📥  RECEIVER
    Name                UZAIR TARIQ
    Phone / Account     031--------
════════════════════════════════════════════════════════
```

---

## ✨ Features

- 🖼️ **Native file explorer** — GUI dialog to select any receipt image
- 🔍 **OCR preprocessing pipeline** — 3× upscale, greyscale, contrast boost, sharpening for maximum accuracy
- 📦 **Extracts all key fields** — status, amount, date/time, reference number, sender, receiver, bank
- 🏦 **Multi-bank support** — Meezan Bank, EasyPaisa, JazzCash, HBL, UBL, MCB, Allied Bank
- 🎨 **Colour-based bank detection** — identifies bank from dominant hues even when watermark text isn't OCR-readable
- 🧹 **Noise filtering** — strips logo artefacts (`oO`, `Nee`, `Nes`) that Tesseract picks up from app icons
- 💻 **Fully offline** — no API calls, no internet required

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `pytesseract` | OCR engine wrapper |
| `Pillow (PIL)` | Image loading & preprocessing |
| `tkinter` | Native file explorer dialog |
| `Tesseract-OCR` | Underlying OCR binary |
| `re` | Regex-based field extraction |

---

## ⚙️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/Uzair3112/receipt-ocr-extractor.git
cd receipt-ocr-extractor
```

### 2. Install Python dependencies
```bash
pip install pillow pytesseract
```

### 3. Install Tesseract binary

**Windows**
Download and run the installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
Then uncomment and set the path at the top of `receipt_extractor.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Linux (Ubuntu / Debian)**
```bash
sudo apt install tesseract-ocr
```

**macOS**
```bash
brew install tesseract
```

---

## 🚀 Usage

```bash
python receipt_extractor.py
```

1. A file explorer dialog opens — select your receipt image (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.webp`)
2. OCR runs with optimised preprocessing
3. Extracted data is printed to the terminal in a formatted table

---

## 🔬 How It Works

```
Image Selected
      │
      ▼
Preprocessing
  ├── 3× upscale (LANCZOS)
  ├── Greyscale conversion
  ├── Contrast ×2.5
  └── Sharpness ×2.0 + SHARPEN filter
      │
      ▼
Tesseract OCR  (--oem 3 --psm 3)
      │
      ▼
Regex Parser
  ├── Status detection
  ├── Amount  (PKR / Rs. variants)
  ├── Date & Time
  ├── Reference Number
  ├── Sender Name + Phone
  ├── Receiver Name + Phone
  └── Bank identification
        ├── Keyword scan (OCR text)
        └── Colour heuristic (dominant hue sampling)
      │
      ▼
Formatted Terminal Output
```

**Why PSM 3?** Tesseract's Page Segmentation Mode 3 (fully automatic layout analysis) outperforms PSM 6 (uniform block) on receipt images because receipts have mixed layout regions — a large amount block, watermark layer, and compact sender/receiver rows. PSM 3 handles all three correctly.

---

## 📁 Project Structure

```
receipt-ocr-extractor/
│
├── image_recognition.py   # Main script
└── README.md              # This file
```

---

## 🧩 Supported Receipt Formats

Tested and working with:

- ✅ EasyPaisa (send money receipts)
- ✅ Meezan Bank (mobile app transfers)
- ✅ JazzCash (P2P transfer receipts)
- 🔄 HBL / UBL / MCB / Allied Bank (keyword detection supported)

---

## 🤝 Contributing

Pull requests are welcome. To add support for a new bank or receipt layout:

1. Add a keyword entry in the `keywords` dict inside `parse()`
2. If the bank uses a distinct colour scheme, extend `detect_bank()`
3. Test with a sample receipt and open a PR

---

## 👤 Author

**Uzair Tariq**
BS Data Science — University of the Punjab, Lahore (2023–2027)
---
