import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models import SchemeRequest, SchemeResponse, ChatRequest, ChatResponse, OfficeResponse
from app.services.recommendation import recommendation_engine

# Need these for lazy loading
from app.utils.loader import loader
from app.services.rag import rag_engine
from app.services.chatbot import chatbot_engine
from app.services.pdf_parser import pdf_parser_agent
from app.utils.hashing import generate_file_hash
from app.services.blockchain import BlockchainService

# For hackathon demo, using a default instance (needs environment variable or fund generated address)
# You can set ALGORAND_MNEMONIC in your environment
blockchain_service = BlockchainService(os.getenv("ALGORAND_MNEMONIC"))


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

@router.get("/nearest-offices", response_model=List[OfficeResponse])
def get_nearest_offices(lat: float, lng: float):
    """
    Finds and returns the nearest government offices (BDO, CSC)
    based on user latitude and longitude.
    """
    # Simple validation for coordinates
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid coordinates. Lat must be -90 to 90, Lng -180 to 180.")

    # Import the service
    from app.services.office_service import office_service
    
    # Get top 5 nearest offices
    results = office_service.get_nearest_offices(lat, lng, limit=5)
    
    return results

@router.post("/blockchain/store-hash")
async def store_doc_hash(file: UploadFile = File(...)):
    """
    Hashes the uploaded document and stores it on the Algorand blockchain.
    """
    try:
        file_bytes = await file.read()
        doc_hash = generate_file_hash(file_bytes)
        
        # Store on Algorand
        blockchain_result = blockchain_service.store_hash(doc_hash)
        
        return {
            "status": "success",
            "message": "Document hash successfully notarized on Algorand Testnet.",
            **blockchain_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain Error: {str(e)}")

@router.post("/blockchain/verify-doc")
async def verify_doc_integrity(tx_id: str, file: UploadFile = File(...)):
    """
    Verifies the uploaded document against a hash stored in a blockchain transaction.
    """
    try:
        file_bytes = await file.read()
        current_hash = generate_file_hash(file_bytes)
        
        # Verify on Algorand
        is_verified, result = blockchain_service.verify_hash(tx_id, current_hash)
        
        if is_verified:
            return {
                "status": "verified",
                **result,
                "tx_id": tx_id,
                "explorer_url": f"https://testnet.algoscan.app/tx/{tx_id}"
            }
        else:
            # Handle error message vs structured failure dict
            if isinstance(result, dict):
                return {
                    "status": "failed",
                    **result,
                    "tx_id": tx_id,
                    "explorer_url": f"https://testnet.algoscan.app/tx/{tx_id}"
                }
            else:
                return {
                    "status": "error",
                    "message": result,
                    "tx_id": tx_id
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification Error: {str(e)}")

