from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from app.db.session import Base

class VerificationRecord(Base):
    __tablename__ = "verification_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # User Input
    name_input = Column(String, index=True)
    id_input = Column(String, index=True)
    dob_input = Column(String)
    
    # Analysis Results (Stored as JSON)
    audit_report = Column(JSON)  # The match scores
    taxonomy = Column(JSON)      # Error counts
    ocr_data = Column(JSON)      # Raw text extracted
    
    # File Metadata (Good for debugging)
    filename = Column(String, nullable=True)