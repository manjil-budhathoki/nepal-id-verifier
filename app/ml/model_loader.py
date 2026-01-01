from app.ml.detection.yolo import load_model as load_yolo
from app.ml.ocr.engines import load_engines as load_ocr

def preload_models():
    """
    Call this on app startup.
    This ensures models are in RAM before the first request hits.
    """
    print("--- STARTING MODEL PRELOAD ---")
    load_yolo()
    load_ocr()
    print("--- MODEL PRELOAD COMPLETE ---")