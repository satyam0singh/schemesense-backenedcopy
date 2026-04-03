from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class SchemeRequest(BaseModel):
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    gender: Optional[str] = None
    state: Optional[str] = None

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
