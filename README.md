# ID Verification & Audit System (Nepal)

A hybrid OCR and object detection pipeline designed to verify Nepali Citizenship IDs against user input. It handles both English and Nepali (Devanagari) scripts, performs cross-calendar conversion (AD/BS), and uses phonetic skeleton matching for name verification.

## ⚡ Key Capabilities

* **Object Detection:** Identifies ID cards and crops regions (Photo, Text Blocks) using YOLOv8.
* **Hybrid OCR:** Uses **PaddleOCR** (v3/v4) for Nepali/English and **Doctr** as an English fallback.
* **Dual-Script Verification:** Matches user input (English) against ID text (Nepali) using phonetic consonant skeleton algorithms.
* **Date Conversion:** Automatically validates Dates of Birth by converting between AD and BS (Nepali) calendars.
* **Architecture:** Decoupled architecture with **FastAPI** (Backend/Model Server) and **Streamlit** (Frontend/UI).

## 🛠 Tech Stack

* **Language:** Python 3.10
* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **ML/OCR:** Ultralytics YOLOv8, PaddleOCR, Doctr, OpenCV
* **Logic:** `nepali_datetime`, `difflib` (Fuzzy matching)

## 📂 Project Structure

```text
/
├── backend.py            # FastAPI Model Server (Handles heavy lifting)
├── app.py                # Streamlit Client (UI)
├── models/               # YOLO .pt files
├── src/
│   ├── detection/        # YOLO inference logic
│   ├── ocr/              # OCR engines (Paddle/Doctr) & logic
│   ├── extraction/       # Field matching & verification logic
│   └── utils/            # Image preprocessing
└── requirements.txt      # Project dependencies
```

## 🚀 Installation

1. **Clone & Environment**

    ```bash
    conda create -n id_verify_env python=3.10
    conda activate id_verify_env
    pip install -r requirements.txt
    ```

2. **System Dependencies (Linux)**
    PaddleOCR requires specific libraries.

    ```bash
    sudo apt-get install libgl1-mesa-glx libgomp1
    ```

## 🏃‍♂️ How to Run

This project requires two terminals running simultaneously.

**Terminal 1: Start the Backend (API)**
This loads the ML models into memory.

```bash
python -m uvicorn backend:app --reload --port 8000
```

*Wait until you see "Application startup complete".*

**Terminal 2: Start the Frontend (UI)**

```bash
streamlit run app.py
```
Access the UI at `http://localhost:8501`.

## ⚠️ Important Configuration

**PaddleOCR Instability on Linux:**
To prevent C++ crashes (`std::exception`), specific environment variables are forced in `backend.py`. **Do not remove these lines:**

```python

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"
```

## 📝 Usage logic

1. **Frontend:** User enters Name, ID, and DOB, and uploads an image.
2. **API:** Image is sent to FastAPI.
3. **Pipeline:**
    * Image is converted to RGB & Contiguous Memory.
    * YOLO crops the ID.
    * PaddleOCR extracts Raw Text.
    * `field_extractor.py` performs Consonant Skeleton matching (e.g., "Manjil" == "मन्जिल").
4. **Result:** JSON report is returned with match scores (0-100%).