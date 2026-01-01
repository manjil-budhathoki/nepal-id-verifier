import cv2
import numpy as np
from app.ml.ocr.engines import get_paddle_ne, get_paddle_en

def ensure_rgb(image):
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    return image

# ... KEEP THE parse_paddle_result FUNCTION AS IS ...
def parse_paddle_result(results):
    # (Keep the robust version we wrote in the previous step)
    text_list = []
    if not results: return ""
    if isinstance(results, list):
         for res in results:
            if hasattr(res, 'keys') and 'rec_texts' in res:
                text_list.extend(res['rec_texts'])
                continue
            if hasattr(res, 'rec_texts') and res.rec_texts:
                text_list.extend(res.rec_texts)
                continue
            if isinstance(res, list):
                for line in res:
                    if len(line) == 2 and isinstance(line[1], tuple):
                         text_list.append(line[1][0])
                    elif isinstance(line, tuple) and len(line) == 2:
                        text_list.append(line[0])
    return " ".join(text_list).strip()

def run_ocr(target):
    script = target.get("script", "english")
    raw_crop = target.get("processed_crop")
    
    if raw_crop is None or raw_crop.size == 0:
         return {"text": "", "engine": "error", "confidence_flag": "empty_crop"}

    crop = ensure_rgb(raw_crop)
    crop = np.ascontiguousarray(crop)

    result = {"text": "", "engine": "", "confidence_flag": "normal"}

    # SIMPLIFIED LOGIC: PADDLE ONLY
    if script == "english":
        # Use English model for Back of card
        reader = get_paddle_en()
        engine = "paddle_en"
    else:
        # Use Nepali model for Front of card
        # (Note: Nepali model handles English characters reasonably well too)
        reader = get_paddle_ne()
        engine = "paddle_ne"

    try:
        # Use default OCR call (includes detection + recognition)
        # We trust the V5 parser to handle the result
        paddle_results = reader.ocr(crop)
        
        # Debug print if you still want it
        # print(f"DEBUG RAW PADDLE: {paddle_results}")
        
        text = parse_paddle_result(paddle_results)
    except Exception as e:
        print(f"Paddle Error ({engine}): {e}")
        text = ""

    result["text"] = text
    result["engine"] = engine
    return result