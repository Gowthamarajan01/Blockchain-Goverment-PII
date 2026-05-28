from pydantic import BaseModel
from typing import List, Optional

class ScanRequest(BaseModel):
    text: str

class PIIDetection(BaseModel):
    type: str
    value: str
    start: int
    end: int
    confidence: float
    method: str
    sensitivity: str

class ScanResponse(BaseModel):
    original_text: str
    masked_text: str
    pii_found: List[PIIDetection]
    status: str
    saved_to: Optional[str] = None

class MaskRequest(BaseModel):
    text: str
    pii_list: List[PIIDetection]

class LogEntry(BaseModel):
    file_name: str
    pii_types: List[str]
    count: int
    timestamp: str
    user_id: str
