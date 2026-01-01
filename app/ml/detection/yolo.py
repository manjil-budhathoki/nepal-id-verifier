import cv2
import numpy as np

from ultralytics import YOLO

from app.core.config import settings

# Global Model Variable
_YOLO_MODEL = None

def load_model():
    "Explicitly called during startup"

    global _YOLO_MODEL
    print(f"Loading YOLO from {settings.YOLO_MODEL_PATH}...")
    _YOLO_MODEL = YOLO(settings.YOLO_MODEL_PATH)


def get_model():
    "Getter that ensures model is loaded"

    if _YOLO_MODEL is None:
        load_model()
    return _YOLO_MODEL

def detect_regions(image: np.ndarray, conf_threshold: float = 0.3):

    model = get_model()

    # verbose = false prevents clusttering producction logs.

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
            "bbox": [x1, y1, x2, y2],
            "crop": image[y1:y2, x1:x2]
        })
    return detections

def process_cards(detections, img_shape):
    """
    Groups detections into logical cards.
    Handles Single Card, Composite (Front+Back), and Fallback cases.
    """
    height, width = img_shape[:2]
    
    # 1. Identify key features for Heuristic Splitting
    photo = next((d for d in detections if d["label"] == "photo_region"), None)
    fingerprint = next((d for d in detections if d["label"] == "fingerprint_region"), None)
    
    boundaries = [d for d in detections if d["label"] == "Id_card_boundary"]
    
    # --- SMART SPLIT LOGIC ---
    # If we see BOTH Photo (Front) and Fingerprint (Back) significantly separated,
    # we force a split, ignoring whatever the 'Id_card_boundary' detection says.
    is_composite = False
    
    if photo and fingerprint:
        # Calculate Y-centers
        py = (photo["bbox"][1] + photo["bbox"][3]) / 2
        fy = (fingerprint["bbox"][1] + fingerprint["bbox"][3]) / 2
        
        # If separated by at least 15% of image height
        if abs(py - fy) > height * 0.15:
            is_composite = True
            # Determine split line (midpoint between the two features)
            split_y = int((py + fy) / 2)
            
            # Create two Virtual Boundaries
            # Card 1 (Top)
            b1 = {
                "bbox": (0, 0, width, split_y), 
                "conf": 1.0, 
                "label": "virtual_boundary"
            }
            # Card 2 (Bottom)
            b2 = {
                "bbox": (0, split_y, width, height), 
                "conf": 1.0, 
                "label": "virtual_boundary"
            }
            boundaries = [b1, b2]
            print("DEBUG: Smart Split Triggered (Composite Image detected)")

    # 2. Fallback: If no boundaries and not composite, assume whole image
    if not boundaries:
        boundaries = [{"bbox": (0, 0, width, height), "conf": 0.0, "label": "fallback_boundary"}]

    cards = []
    for boundary in boundaries:
        bx1, by1, bx2, by2 = boundary["bbox"]
        
        # Find detections that belong to this boundary
        card_regions = []
        for d in detections:
            # Skip the boundary boxes themselves
            if d["label"] in ["Id_card_boundary", "virtual_boundary", "fallback_boundary"]: 
                continue
            
            dx1, dy1, dx2, dy2 = d["bbox"]
            cx, cy = (dx1 + dx2) / 2, (dy1 + dy2) / 2
            
            # Check if detection center is inside boundary
            if bx1 <= cx <= bx2 and by1 <= cy <= by2:
                card_regions.append(d)
        
        # Determine Face (Front/Back) based on content
        labels = [r["label"] for r in card_regions]
        
        face = "unknown"
        if "photo_region" in labels:
            face = "front"
        elif "fingerprint_region" in labels:
            face = "back"
        else:
            # Secondary heuristic: If we split strictly, we can guess based on position?
            # For now, let's trust the features. If a card has neither, it might be text only.
            # If we used Smart Split, we know Top is likely Photo(Front) and Bottom is Print(Back)
            if is_composite:
                # If this boundary is the Top one (by1 == 0) and has photo
                if by1 == 0 and photo: face = "front"
                # If this boundary is Bottom one and has fingerprint
                if by1 > 0 and fingerprint: face = "back"

        cards.append({
            "face": face,
            "regions": card_regions,
            "bbox": (bx1, by1, bx2, by2),
            "presence_map": labels
        })
    
    return cards