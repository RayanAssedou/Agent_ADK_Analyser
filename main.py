import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Trading Strategy AI Analyzer API",
    description="AI-powered trading strategy analysis using Claude and team agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Replit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """API root endpoint with available endpoints"""
    return {
        "message": "Trading Strategy AI Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": {
                "url": "/api/analyze",
                "method": "POST",
                "description": "Analyze strategy with Claude"
            },
            "analyze_comprehensive": {
                "url": "/api/analyze-comprehensive", 
                "method": "POST",
                "description": "Comprehensive analysis with AI team"
            },
            "validate_csv": {
                "url": "/api/validate-csv",
                "method": "POST", 
                "description": "Validate CSV file structure"
            },
            "reports": {
                "url": "/api/reports",
                "method": "GET",
                "description": "List all analysis reports"
            },
            "report": {
                "url": "/api/reports/{filename}",
                "method": "GET",
                "description": "Get specific report content"
            },
            "strategies": {
                "url": "/api/strategies",
                "method": "GET",
                "description": "List stored strategies"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Trading Strategy AI Analyzer"}

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("storage/uploads", exist_ok=True)
    os.makedirs("storage/chromadb_store", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )