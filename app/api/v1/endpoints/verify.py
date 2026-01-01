from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.verifier import process_verification
from app.schemas.verification import VerificationResponse

router = APIRouter()

@router.post("/verify", response_model=VerificationResponse)
def verify_id(
    file: UploadFile = File(...),
    name: str = Form(...),
    id_number: str = Form(...),
    dob: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Validation
    # validation: content_type might be None (Streamlit behavior)
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    # 2. Call Service
    try:
        # Read file into memory (be careful with large files in prod, but ok for ID cards)
        file_bytes = file.file.read()
        
        result = process_verification(
            file_bytes=file_bytes,
            user_data={"name": name, "id_number": id_number, "dob": dob},
            db=db,
            filename=file.filename
        )
        return result

    except Exception as e:
        # Log this error in production!
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))