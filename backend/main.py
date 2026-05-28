from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from typing import List
from datetime import datetime

from backend.services.pii_detector import PIIDetector
from backend.services.ocr_service import OCRService
from backend.services.masking_service import MaskingService
from backend.models.schemas import ScanRequest, ScanResponse, PIIDetection
from backend.utils.db import log_scan, get_logs, clear_logs
from backend.utils.auth import create_access_token, verify_password, get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(title="HideX - Secure PII Guard")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock User for Demonstration
USER_DB = {
    "admin": get_password_hash("admin123")
}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_hash = USER_DB.get(form_data.username)
    if not user_hash or not verify_password(form_data.password, user_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/scan-text", response_model=ScanResponse)
async def scan_text(request: ScanRequest):
    text = request.text
    detections = PIIDetector.detect(text)
    
    # Enrich with sensitivity
    for d in detections:
        d["sensitivity"] = PIIDetector.classify_sensitivity(d["type"])
    
    masked_text = MaskingService.mask_text(text, detections)
    
    # Automatically clear previous vault logs for privacy
    clear_logs()
    
    # Log to DB
    log_scan("Raw Text Input", detections)

    # Save to local system file
    save_dir = "data/sanitized"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"sanitized_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(masked_text)
    
    return {
        "original_text": text,
        "masked_text": masked_text,
        "pii_found": detections,
        "status": "success" if detections else "safe",
        "saved_to": save_path
    }

@app.post("/scan-file", response_model=ScanResponse)
async def scan_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text using OCR Service
    text = OCRService.extract_text(file_path)
    
    if not text:
        return {"original_text": "", "masked_text": "", "pii_found": [], "status": "no_text_extracted"}
    
    detections = PIIDetector.detect(text)
    for d in detections:
        d["sensitivity"] = PIIDetector.classify_sensitivity(d["type"])
        
    masked_text = MaskingService.mask_text(text, detections)
    
    # Automatically clear previous vault logs for privacy
    clear_logs()

    # Log to DB
    log_scan(file.filename, detections)
    
    # Save to local system file
    save_dir = "data/sanitized"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"sanitized_{file.filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(masked_text)

    return {
        "original_text": text,
        "masked_text": masked_text,
        "pii_found": detections,
        "status": "success" if detections else "safe",
        "saved_to": save_path
    }

@app.get("/logs")
async def fetch_logs():
    return get_logs()

@app.delete("/logs")
async def erase_logs():
    try:
        clear_logs()
        return {"status": "vault_erased"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to HideX - Secure PII Guard"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
