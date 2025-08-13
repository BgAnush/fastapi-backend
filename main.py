from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Create FastAPI app instance
app = FastAPI(
    title="Namma Raitha Backend",
    description="FastAPI backend for Farmer-Retailer mobile application",
    version="1.0.0",
)

# ✅ Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:3000",
        "http://192.168.31.63:8081",
        "http://172.18.128.58:8081",
        "http://172.18.128.58:3000",
        "*"  # Allow all origins (caution in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Import routers directly from same directory
import signup
import login
import add_produce
import farmer
import retailer

# ✅ Register routers
app.include_router(signup.router, prefix="/auth", tags=["auth"])
app.include_router(login.router, prefix="/auth", tags=["auth"])
app.include_router(add_produce.router, prefix="/produce", tags=["produce"])
app.include_router(farmer.router, prefix="/farmer", tags=["farmer"])
app.include_router(retailer.router, tags=["retailer"])

# ✅ Health check
@app.get("/")
async def root():
    return {"message": "Namma Raitha Backend is running"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# ✅ Debug: List all routes
@app.get("/routes")
async def list_routes():
    return {
        "registered_routes": [
            {"path": route.path, "methods": list(route.methods)}
            for route in app.routes
        ]
    }
