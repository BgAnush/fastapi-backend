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
    "*",  # Caution: allow all origins in production only if necessary
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Import and include routers =====
try:
    from signup import router as signup_router
    app.include_router(signup_router, prefix="/auth")
    print("✅ Signup router imported successfully")
except ImportError as e:
    print(f"⚠️ Failed to import signup router: {e}")

try:
    from login import router as login_router
    app.include_router(login_router, prefix="/auth")
    print("✅ Login router imported successfully")
except ImportError as e:
    print(f"⚠️ Failed to import login router: {e}")

try:
    from add_produce import router as add_produce_router
    app.include_router(add_produce_router)
    print("✅ Produce router imported successfully")
except ImportError as e:
    print(f"❌ Failed to import produce router: {e}")

try:
    from farmer import router as farmer_router
    app.include_router(farmer_router, prefix="/farmer")
    print("✅ Farmer router imported successfully")
except ImportError as e:
    print(f"⚠️ Failed to import farmer router: {e}")

try:
    from retailer import router as retailer_router
    app.include_router(retailer_router)  # Prefix is handled in retailer.py
    print("✅ Retailer router imported successfully")
except Exception as e:
    print(f"❌ Failed to import retailer router: {e}")

# ===== Health Check Routes =====
@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/test")
def test_endpoint():
    """Test endpoint to verify base URL is working"""
    return {
        "message": "API is running",
        "endpoints": {
            "retailer_test": "/retailer/test",
            "produce_list": "/retailer/produce/list"
        }
    }

@app.get("/")
def root():
    return {"message": "✅ FastAPI backend is running"}