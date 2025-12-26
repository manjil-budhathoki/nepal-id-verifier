# src/utils/image_utils.py

import cv2
import numpy as np
from PIL import Image, ImageOps
import io

def prepare_image(uploaded_file):
    """Standardizes input: orientation, RGB, and metadata."""
    file_bytes = uploaded_file.getvalue()
    raw_img = Image.open(io.BytesIO(file_bytes))
    img = ImageOps.exif_transpose(raw_img).convert("RGB")
    img_array = np.array(img)
    
    metadata = {
        "filename": uploaded_file.name,
        "size": f"{img.width}x{img.height}",
        "filesize_kb": round(len(file_bytes) / 1024, 2)
    }
    return img_array, metadata

def clean_for_ocr(crop):
    """
    Preprocessing: CLAHE + Mild Sharpening.
    FIX 1: Reduced denoising to prevent text erasure ([No Text] issue).
    FIX 2: Converts back to RGB so PaddleOCR doesn't crash.
    """
    # 1. Convert to Gray for processing
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop
        

    # 2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)
    
    # 3. Light Denoising (Reduced strength from 10 to 3 to keep text sharp)
    denoised = cv2.fastNlMeansDenoising(contrasted, None, 3, 7, 21)
    
    # 4. Sharpening
    gaussian = cv2.GaussianBlur(denoised, (0, 0), 3)
    sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)

    # 5. CRITICAL FIX: Convert back to RGB for PaddleOCR
    sharpened_rgb = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

    stats = {
        "mean": round(float(np.mean(sharpened)), 2),
        "variance": round(float(np.var(sharpened)), 2)
    }
    
    return sharpened_rgb, stats