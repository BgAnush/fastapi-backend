from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Namma Raitha Backend",
    description="FastAPI backend for Farmer-Retailer mobile application",
    version="1.0.0",
)

# Allowed CORS origins
origins = [
    "http://localhost:8081",
    "http://localhost:3000",
    "http://192.168.31.63:8081",
    "http://172.18.128.58:8081",
    "http://172.18.128.58:3000",
    "*",  # For testing only
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from retailer import router as retailer_router
app.include_router(
    retailer_router,
    prefix="/retailer",
    tags=["Retailer"]
)

# Health check endpoints
@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/")
def root():
    return {"message": "✅ FastAPI backend is running"}

@app.post("/retailer/test")
async def test_route():
    return {"message": "Test route works"}