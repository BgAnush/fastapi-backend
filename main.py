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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:3000",
        "http://192.168.31.63:8081",
        "http://172.18.128.58:8081",
        "http://172.18.128.58:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers with explicit error handling
routers = [
    ("auth.signup", "/auth"),
    ("auth.login", "/auth"),
    ("produce.add_produce", ""),
    ("farmer", "/farmer"),
    ("retailer", "/retailer")  # Now using explicit prefix here
]

for module, prefix in routers:
    try:
        router = __import__(module, fromlist=["router"]).router
        app.include_router(router, prefix=prefix)
        print(f"✅ {module} router registered at {prefix or '/'}")
    except Exception as e:
        print(f"❌ Failed to import {module} router: {str(e)}")

# Health check endpoints
@app.get("/")
async def root():
    return {"message": "Namma Raitha Backend is running"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/routes")
async def list_routes():
    return {
        "registered_routes": [
            {"path": route.path, "methods": route.methods}
            for route in app.routes
        ]
    }