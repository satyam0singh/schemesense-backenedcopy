from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class SchemeRequest(BaseModel):
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    startup_stage: Optional[str] = None
    startup_recognition: Optional[str] = None

class SchemeResponse(BaseModel):
    scheme_name: str
    eligible: bool
    confidence_score: float
    match_reason: str
    benefits: str
    application_link: str
    category: str
    documents_required: List[str]
    match_type: str
    priority_tag: str

class ChatRequest(BaseModel):
    query: str
    scheme: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    schemes: Optional[List[Dict[str, Any]]] = None
    related_schemes: Optional[List[Dict[str, Any]]] = None

class OfficeResponse(BaseModel):
    name: str
    type: str
    lat: float
    lng: float
    address: str
    distance: float

class DocumentRecord(BaseModel):
    name: str
    hash: str

class VerifiedApplicationRequest(BaseModel):
    user: str
    scheme: str
    documents: List[DocumentRecord]
    documents_verified: bool
    timestamp: Optional[str] = None

class VerifiedApplicationResponse(BaseModel):
    tx_id: str
    explorer_url: str
    record: Dict[str, Any]
    timestamp: str
