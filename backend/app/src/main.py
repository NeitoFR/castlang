from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import router
from src.database import create_tables
from src.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application configuration from environment variables
APP_TITLE = os.getenv("APP_TITLE", "CastLang API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app = FastAPI(title=APP_TITLE, version=APP_VERSION, debug=DEBUG)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # Create database tables
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=APP_HOST, 
        port=APP_PORT,
        reload=DEBUG
    ) 