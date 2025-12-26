import os
# --- CRITICAL: Set Flags BEFORE importing libraries ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_allocator_strategy"] = "auto_growth"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import cv2
import numpy as np
import json
from io import BytesIO
from PIL import Image, ImageOps

# Import your existing logic
from src.detection.yolo_detector import detect_regions, process_cards, prepare_ocr_targets, load_yolo_model
from src.ocr.engine_factory import get_doctr_model, get_easyocr_ne, get_easyocr_en
from src.ocr.processor import run_ocr
from src.ocr.normalizer import process_robust_text
from src.extraction.field_extractor import extract_structured_data

# --- LIFESPAN MANAGER (Load Models on Startup) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Loading Models...")
    # Trigger model loading
    load_yolo_model()
    get_doctr_model()
    get_easyocr_ne()
    get_easyocr_en()
    print("✅ Models Loaded & Ready!")
    yield
    print("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan)

# Allow Streamlit to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HELPER: Process Image ---
def read_imagefile(file_data) -> np.ndarray:
    image = Image.open(BytesIO(file_data))
    image = ImageOps.exif_transpose(image).convert("RGB")
    return np.array(image)

# --- API ENDPOINT ---
@app.post("/verify")
async def verify_id(
    file: UploadFile = File(...),
    name: str = Form(...),
    id_number: str = Form(...),
    dob: str = Form(...)
):
    try:
        # 1. Read Image
        file_content = await file.read()
        img_array = read_imagefile(file_content)
        
        # 2. Detection
        raw_detections = detect_regions(img_array)
        cards = process_cards(raw_detections, img_array.shape)
        
        all_ocr_results = []

        # 3. Processing Loop (Same logic as before)
        for i, card in enumerate(cards):
            targets = prepare_ocr_targets(card)
            
            for target in targets:
                # Add Padding
                raw_crop = target["crop"]
                processed_crop = cv2.copyMakeBorder(
                    raw_crop, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255]
                )
                target["processed_crop"] = processed_crop
                
                # Run OCR
                ocr_result = run_ocr(target)
                raw_text = ocr_result["text"]
                normalized_text = process_robust_text(raw_text)
                
                all_ocr_results.append({
                    "face": card["face"],
                    "raw_text": raw_text,
                    "text": normalized_text,
                    "metadata": target["metadata"],
                    "engine": ocr_result["engine"]
                })

        # 4. Audit Logic
        user_data = {"name": name, "id_number": id_number, "dob": dob}
        audit_report = extract_structured_data(all_ocr_results, user_data)
        
        # 5. Taxonomy Stats
        tax_counts = {}
        for f_data in audit_report.values():
            e_type = f_data['error_type']
            tax_counts[e_type] = tax_counts.get(e_type, 0) + 1

        return {
            "status": "success",
            "report": audit_report,
            "taxonomy": tax_counts,
            "ocr_details": [
                {"engine": r['engine'], "text": r['text'], "raw": r['raw_text']} 
                for r in all_ocr_results
            ]
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "running"}