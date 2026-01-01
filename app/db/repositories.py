from sqlalchemy.orm import Session
from app.db.models import VerificationRecord
import json

def create_verification_record(
    db: Session,
    name: str,
    id_number: str,
    dob: str,
    audit_report: dict,
    taxonomy: dict,
    ocr_data: list,
    filename: str = None
):
    """Saves a new verification attempt."""
    
    # JSON serialization happens automatically by SQLAlchemy for JSON columns,
    # but depending on the driver, ensuring dicts are passed is safer.
    
    db_record = VerificationRecord(
        name_input=name,
        id_input=id_number,
        dob_input=dob,
        audit_report=audit_report,
        taxonomy=taxonomy,
        ocr_data=ocr_data,
        filename=filename
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_recent_records(db: Session, limit: int = 50):
    """Fetches history for the dashboard."""
    return db.query(VerificationRecord).order_by(VerificationRecord.id.desc()).limit(limit).all()