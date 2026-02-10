# Make the Entry point of the application
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modules
from routes.contract import router as contract_router
from routes.regulations import router as regulations_router
from routes.ai_insights import router as ai_insights_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Legal Guard RegTech API",
    description="AI-powered legal document analysis and compliance checking platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175"
    ],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contract_router)
app.include_router(regulations_router)
app.include_router(ai_insights_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Legal Guard RegTech API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/contracts/health"
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


