from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

# Request body model
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    name: str
    role: str  # Must be 'farmer' or 'retailer'

@router.post("/signup")
async def signup_user(user: SignupRequest):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if user.role not in ["farmer", "retailer"]:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    # Sign up user using Supabase Auth (only email and password)
    try:
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

    if auth_response.user is None:
        raise HTTPException(status_code=400, detail="Signup failed. Email may already be in use.")

    user_id = auth_response.user.id  # UUID from Supabase Auth

    # Insert additional details into profiles table
    # Ensure your Supabase RLS policies allow inserting with auth.uid() = id
    data = {
        "id": user_id,
        "email": user.email,
        "password": user.password,  # Optional: hash this if stored manually
        "name": user.name,
        "role": user.role,
    }

    try:
        response = supabase.table("profiles").insert(data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")

    if response.data:
        return {"message": "User registered successfully!"}
    else:
        raise HTTPException(status_code=500, detail="Failed to insert user profile.")
