import cv2
import uuid
import os
import numpy as np
from sqlalchemy.orm import Session
from PIL import Image, ImageOps
import io

# Imports from our new layers
from app.ml.detection.yolo import detect_regions, process_cards
from app.ml.ocr.pipeline import run_ocr
from app.utils.text import process_robust_text
from app.services.auditor import generate_audit_report
from app.db.repositories import create_verification_record

def prepare_image(file_bytes):
    image = Image.open(io.BytesIO(file_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")

    max_dimension = 1800
    if max(image.size) > max_dimension:
        # Calculate new size maintaining aspect ratio
        scale = max_dimension / max(image.size)
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

        # print(f"DEBUG: Resized image to {new_size}")
    # ---------------------------------------
    return np.array(image)

def process_verification(file_bytes: bytes, user_data: dict, db: Session, filename: str = None):
    # 1. Read Image
    img_array = prepare_image(file_bytes)
    
    # 2. Detection (YOLO)
    raw_detections = detect_regions(img_array)
    cards = process_cards(raw_detections, img_array.shape)
    
    all_ocr_results = []

    # 3. Processing Loop
    for card in cards:
        script = "english" if card["face"] == "back" else "nepali"
        
        # Filter for text regions
        text_regions = [d for d in card["regions"] if d["label"] == "text_block_primary"]
        
        # DEBUG: Print how many regions were found
        print(f"DEBUG: Found {len(text_regions)} text blocks on {card['face']} face.")

        for region in text_regions:
            x1, y1, x2, y2 = region["bbox"]
            raw_crop = img_array[y1:y2, x1:x2]
            
            # Add padding
            processed_crop = cv2.copyMakeBorder(
                raw_crop, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255]
            )
            
            # --- DEBUG: SAVE CROP TO DISK ---
            debug_filename = f"debug_crops/{script}_{uuid.uuid4().hex[:6]}.jpg"
            # cv2 expects BGR, but we have RGB. Convert for saving.
            cv2.imwrite(debug_filename, cv2.cvtColor(processed_crop, cv2.COLOR_RGB2BGR))
            print(f"DEBUG: Saved crop to {debug_filename}")
            # -------------------------------
            
            target = {
                "script": script,
                "processed_crop": processed_crop,
                "metadata": {"box": region["bbox"]}
            }
            
            # Run OCR
            ocr_result = run_ocr(target)
            
            # ... rest of the loop remains same ...
            raw_text = ocr_result["text"]
            normalized_text = process_robust_text(raw_text)
            
            all_ocr_results.append({
                "face": card["face"],
                "raw_text": raw_text,
                "text": normalized_text,
                "engine": ocr_result["engine"],
                "conf_flag": ocr_result.get("confidence_flag", "unknown")
            })


    # 4. Audit (Compare Logic)
    audit_report, taxonomy = generate_audit_report(all_ocr_results, user_data)
    
    # 5. Save to DB
    create_verification_record(
        db=db,
        name=user_data["name"],
        id_number=user_data["id_number"],
        dob=user_data["dob"],
        audit_report=audit_report,
        taxonomy=taxonomy,
        ocr_data=all_ocr_results,
        filename=filename
    )
    
    return {
        "report": audit_report,
        "taxonomy": taxonomy,
        "ocr_details": all_ocr_results
    }