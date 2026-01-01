from paddleocr import PaddleOCR
from app.core.config import settings

# Global instances
_PADDLE_NE = None
_PADDLE_EN = None
def load_engines():
    """Loads all OCR engines into memory."""
    global _PADDLE_NE, _PADDLE_EN, _DOCTR

    print("Loading Paddle (NE)...")
    _PADDLE_NE = PaddleOCR(
        lang='ne', 
        # Explicitly disable dangerous features for CPU
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False, # We keep this one
        # use_angle_cls=False,          # <--- REMOVED (Conflicting Argument)
        enable_mkldnn=False,            # <--- Disable MKLDNN to prevent crashes
        # use_gpu=False,                  # <--- Ensure CPU mode
        rec_batch_num=1   
    )
    
    print("Loading Paddle (EN)...")
    _PADDLE_EN = PaddleOCR(
        lang='en', 
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False, # We keep this one
        # use_angle_cls=False,          # <--- REMOVED (Conflicting Argument)
        enable_mkldnn=False,
        # use_gpu=False,
        rec_batch_num=1
    )

def get_paddle_ne():
    if _PADDLE_NE is None: load_engines()
    return _PADDLE_NE

def get_paddle_en():
    if _PADDLE_EN is None: load_engines()
    return _PADDLE_EN
