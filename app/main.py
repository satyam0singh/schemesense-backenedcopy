from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import router

app = FastAPI(title="Government Scheme Recommendation API")

# Add CORS middleware to allow Flutter frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to flutter app domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}

# Link routers
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # To run locally easily
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
