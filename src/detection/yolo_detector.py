import cv2
import numpy as np
from ultralytics import YOLO
import streamlit as st

@st.cache_resource
def load_yolo_model(model_path="models/yolo/best.pt"):
    """Loads YOLO model once and caches it in memory."""
    return YOLO(model_path)

def detect_regions(image, conf_threshold=0.3):
    """
    Performs the raw YOLO detection pass.
    Returns a list of all detected objects with their crops and bboxes.
    """
    model = load_yolo_model()
    results = model.predict(source=image, conf=conf_threshold, verbose=False)
    
    detections = []
    if not results:
        return detections

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = model.names[int(box.cls[0])]
        detections.append({
            "label": label,
            "conf": float(box.conf[0]),
            "bbox": (x1, y1, x2, y2),
            "crop": image[y1:y2, x1:x2]
        })
    return detections

def process_cards(detections, img_shape):
    """
    Groups detections by ID card and identifies if the card is FRONT or BACK.
    """
    
    boundaries = [d for d in detections if d["label"] == "Id_card_boundary"]
    
    
    if not boundaries:
        boundaries = [{"bbox": (0, 0, img_shape[1], img_shape[0]), "conf": 0.0}]

    cards = []
    for boundary in boundaries:
        bx1, by1, bx2, by2 = boundary["bbox"]
        
        
        card_regions = []
        for d in detections:
            if d["label"] == "Id_card_boundary": continue
            dx1, dy1, dx2, dy2 = d["bbox"]
            cx, cy = (dx1 + dx2) / 2, (dy1 + dy2) / 2
            
            if bx1 <= cx <= bx2 and by1 <= cy <= by2:
                card_regions.append(d)
        
        
        labels = [r["label"] for r in card_regions]
        
        if "photo_region" in labels:
            face = "front"  
        elif "fingerprint_region" in labels:
            face = "back"   
        else:
            face = "unknown"

        cards.append({
            "face": face,
            "regions": card_regions,
            "bbox": (bx1, by1, bx2, by2),
            "presence_map": labels
        })
    
    return cards

def prepare_ocr_targets(card):
    targets = []

    text_labels = ["text_block_primary"] 
    
    script = "english" if card["face"] == "back" else "nepali"

    for det in card["regions"]:
        if det["label"] in text_labels:
            h, w = det["crop"].shape[:2]
            
            targets.append({
                "label": det["label"],
                "script": script,
                "crop": det["crop"],
                "res_warning": f"Low Res ({h}px)" if h < 32 else None,
                "metadata": {"width": w, "height": h, "y": det["bbox"][1]}
            })
    return targets