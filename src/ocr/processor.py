# src/ocr/processor.py
import cv2
import numpy as np
from .engine_factory import get_doctr_model, get_paddleocr_ne, get_paddleocr_en

def ensure_rgb(image):
    """Converts grayscale (2D) to RGB (3D)."""
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    return image

def run_doctr_eng(rgb_crop):
    """Primary English Engine"""
    model = get_doctr_model()
    # Ensure memory is contiguous
    clean_crop = np.ascontiguousarray(rgb_crop)
    input_crop = [clean_crop.astype(np.float32) / 255.0]
    
    result = model(input_crop)
    
    text_segments = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                words = [w.value for w in line.words if w.confidence > 0.3]
                if words:
                    text_segments.append(" ".join(words))
    return " ".join(text_segments).strip()

def parse_paddle_pipeline_result(results):
    """Parses PaddleOCR output (Dict, Object, or List)."""
    text_list = []
    if not results:
        return ""
        
    if isinstance(results, list):
         for res in results:
            # DICTIONARY (New API)
            if isinstance(res, dict) and 'rec_texts' in res:
                text_list.extend(res['rec_texts'])
            # OBJECT (New API Variant)
            elif hasattr(res, 'rec_texts') and res.rec_texts:
                text_list.extend(res.rec_texts)
            # LIST OF LISTS (Legacy API)
            elif isinstance(res, list):
                for line in res:
                    if len(line) == 2 and isinstance(line[1], tuple):
                         text_list.append(line[1][0])

    return " ".join(text_list).strip()

def run_ocr(target):
    script = target["script"]
    raw_crop = target["processed_crop"] 
    
    # 1. Validate Crop
    if raw_crop is None or raw_crop.size == 0 or raw_crop.shape[0] == 0 or raw_crop.shape[1] == 0:
         return {"text": "", "engine": "error", "confidence_flag": "empty_crop"}

    # 2. Ensure Format (RGB + Contiguous)
    crop = ensure_rgb(raw_crop)
    crop = np.ascontiguousarray(crop)

    result = {"text": "", "engine": "", "confidence_flag": "normal"}

    if script == "english":
        text = run_doctr_eng(crop)
        engine = "doctr"
        
        if not text:
            reader = get_easyocr_en()
            try:
                paddle_results = reader.predict(crop)
            except AttributeError:
                paddle_results = reader.ocr(crop, cls=False)
                
            text = parse_paddle_pipeline_result(paddle_results)
            engine = "paddle_en"
            result["confidence_flag"] = "fallback_used"
            
        result["text"] = text
        result["engine"] = engine
    else:
        # Nepali
        reader = get_easyocr_ne()
        try:
            paddle_results = reader.predict(crop)
        except AttributeError:
            paddle_results = reader.ocr(crop, cls=False)
            
        text = parse_paddle_pipeline_result(paddle_results)
        result["text"] = text
        result["engine"] = "paddle_ne"

    return result