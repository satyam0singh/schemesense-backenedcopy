from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import contextlib
import sys
import os

from app.routes import router
from app.utils.loader import loader
from app.services.rag import rag_engine

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("Loading schemes...")
    schemes = loader.load_data()
    
    print("Building FAISS index...")
    rag_engine.build_index(schemes)
    
    print("Startup complete.")
    yield
    # Shutdown actions
    print("Shutting down...")

app = FastAPI(title="Government Scheme Recommendation API", lifespan=lifespan)

# Add CORS middleware to allow Flutter frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to flutter app domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Link routers
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # To run locally easily
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
