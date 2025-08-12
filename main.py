from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Namma Raitha Backend",
    description="FastAPI backend for Farmer-Retailer mobile application",
    version="1.0.0",
)

origins = [
    "http://localhost:8081",
    "http://localhost:3000",
    "http://192.168.31.63:8081",
    "http://172.18.128.58:8081",
    "http://172.18.128.58:3000",
    "*",  # Use with caution in production, restrict as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers with prefixes
try:
    from signup import router as signup_router
    app.include_router(signup_router, prefix="/auth")
except ImportError:
    print("⚠️ Failed to import `signup` router.")

try:
    from login import router as login_router
    app.include_router(login_router, prefix="/auth")
except ImportError:
    print("⚠️ Failed to import `login` router.")

try:
    from add_produce import router as add_produce_router
    app.include_router(add_produce_router)
    print("✅ Produce router imported successfully")
except ImportError as e:
    print(f"❌ Failed to import produce router: {str(e)}")

try:
    from farmer import router as farmer_router
    app.include_router(farmer_router, prefix="/farmer")
except ImportError:
    print("⚠️ Failed to import `farmer` router.")

try:
    from delete import router as delete_router
    app.include_router(delete_router, prefix="/farmer")
    print("✅ Delete router imported successfully")
except ImportError as e:
    print(f"❌ Failed to import delete router: {str(e)}")

try:
    from retailer import router as retailer_router
    app.include_router(retailer_router)
    print("✅ Retailer router imported successfully")
except ImportError as e:
    print(f"❌ Failed to import retailer router: {str(e)}")

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/")
def root():
    return {"message": "✅ FastAPI backend is running"}
