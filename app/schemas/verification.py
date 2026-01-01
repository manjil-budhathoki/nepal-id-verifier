from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class OCRDetail(BaseModel):
    face: str
    raw_text: str
    text: str
    engine: str
    conf_flag: str

class AuditField(BaseModel):
    score: int
    status: str
    span: str
    error_type: str

class VerificationResponse(BaseModel):
    report: Dict[str, AuditField]
    taxonomy: Dict[str, int]
    ocr_details: List[OCRDetail]