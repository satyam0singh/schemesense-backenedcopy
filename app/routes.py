from fastapi import APIRouter
from typing import List
from app.models import SchemeRequest, SchemeResponse
from app.services.recommendation import recommendation_engine

router = APIRouter()

@router.get("/")
def read_root():
    """Root endpoint to welcome users and guide them to documentation."""
    return {"message": "Welcome to SchemeSense API! Navigate to /docs for Swagger documentation."}

@router.get("/health")
def health_check():
    """Health check endpoint to verify backend status"""
    return {"status": "ok", "message": "API is running."}

@router.post("/get-schemes", response_model=List[SchemeResponse])
def get_schemes(user_req: SchemeRequest):
    """
    Main endpoint to get recommended government schemes.
    Takes user criteria, passes it to the RAG + Eligibility + Recommendation engine.
    """
    # Convert Pydantic object to dict, ignoring None values
    user_data = user_req.model_dump(exclude_unset=True)
    
    # Process through the recommendation engine
    results = recommendation_engine.get_recommendations(user_data)
    
    return results
