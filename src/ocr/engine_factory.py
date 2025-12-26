import streamlit as st
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor

@st.cache_resource
def get_doctr_model():
    return ocr_predictor(pretrained=True)

@st.cache_resource
def get_easyocr_ne():
    # Nepali Configuration
    ocr = PaddleOCR(
        lang='ne', 
        # Explicitly disable dangerous features for CPU
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False, # We keep this one
        # use_angle_cls=False,          # <--- REMOVED (Conflicting Argument)
        enable_mkldnn=False,            # <--- Disable MKLDNN to prevent crashes
        # use_gpu=False,                  # <--- Ensure CPU mode
        rec_batch_num=1                 # <--- Process 1 image at a time (safer)
    )
    return ocr

@st.cache_resource
def get_easyocr_en():
    # English Configuration
    ocr = PaddleOCR(
        lang='en', 
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False, # We keep this one
        # use_angle_cls=False,          # <--- REMOVED (Conflicting Argument)
        enable_mkldnn=False,
        # use_gpu=False,
        rec_batch_num=1
    )
    return ocr