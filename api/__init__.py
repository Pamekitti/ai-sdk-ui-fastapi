"""
This file makes the api directory a Python package.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Initialize FastAPI app
app = FastAPI(title="AI SDK UI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routers import chat, chiller_plant

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(chiller_plant.router, prefix="/api/chiller_plant", tags=["chiller_plant"]) 