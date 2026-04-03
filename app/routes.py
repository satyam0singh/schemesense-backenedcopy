from fastapi import APIRouter
from typing import List
from app.models import SchemeRequest, SchemeResponse, ChatRequest, ChatResponse
from app.services.recommendation import recommendation_engine

# Need these for lazy loading
from app.utils.loader import loader
from app.services.rag import rag_engine
from app.services.chatbot import chatbot_engine

router = APIRouter()

initialized = False

def initialize_if_needed():
    global initialized
    if not initialized:
        print("Lazy Loading: Building FAISS Index and loading schemes...")
        schemes = loader.load_data()
        rag_engine.build_index(schemes)
        initialized = True

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
    # Lazy load the ML and FAISS data only when the first request hits
    initialize_if_needed()

    # Convert Pydantic object to dict, ignoring None values
    user_data = user_req.model_dump(exclude_unset=True)
    
    # Process through the recommendation engine
    results = recommendation_engine.get_recommendations(user_data)
    
    return results

@router.post("/chat", response_model=ChatResponse)
def get_chat(chat_req: ChatRequest):
    """
    Simulates an intelligent AI assistant.
    Takes a query string, optional scheme context, and optional user_profile.
    """
    # Lazy load the ML and FAISS data only when the first request hits
    initialize_if_needed()

    user_profile = chat_req.user_profile if chat_req.user_profile else None
    scheme_context = chat_req.scheme if chat_req.scheme else None
    
    return chatbot_engine.chat_pipeline(chat_req.query, scheme_context, user_profile)
