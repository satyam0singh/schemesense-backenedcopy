from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models import SchemeRequest, SchemeResponse, ChatRequest, ChatResponse
from app.services.recommendation import recommendation_engine

# Need these for lazy loading
from app.utils.loader import loader
from app.services.rag import rag_engine
from app.services.chatbot import chatbot_engine
from app.services.pdf_parser import pdf_parser_agent

router = APIRouter()

@router.post("/upload-scheme-pdf")
async def upload_scheme_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, extracts scheme information using Gemini LLM,
    and returns a structured JSON response.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")
    
    try:
        # Read file as bytes
        file_bytes = await file.read()
        
        # Use the PDF Parser Agent to extract structured data
        extracted_data = pdf_parser_agent.pdf_parser_agent(file_bytes)
        
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error during PDF processing: {str(e)}")

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

@router.get("/startups")
def get_all_startups():
    """
    Returns all startup-specific schemes without any eligibility filtering.
    Useful for a dedicated 'Startup Discovery' tab in the app.
    """
    initialize_if_needed()
    all_schemes = loader.schemes
    
    # Filter for schemes where scheme_category contains "Startup" OR ID starts with SCH_STARTUP
    startup_schemes = [
        s for s in all_schemes 
        if any(cat.lower() == "startup" for cat in s.get("scheme_category", [])) or 
           str(s.get("scheme_id", "")).startswith("SCH_STARTUP")
    ]
    
    return startup_schemes
