from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    name: str
    role: str  # 'farmer' or 'retailer'

@router.post("/signup")
def signup_user(user: SignupRequest):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if user.role not in ["farmer", "retailer"]:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    # Sign up user using Supabase Auth
    auth_response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password,
    })

    if auth_response.error:
        raise HTTPException(status_code=400, detail=auth_response.error.message)

    user_data = auth_response.user
    if user_data is None:
        raise HTTPException(status_code=400, detail="Signup failed. Email may already be in use.")

    user_id = user_data.id

    # Insert into profiles without password
    data = {
        "id": user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }

    response = supabase.table("profiles").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {response.error.message}")

    return {"message": "User registered successfully!", "user_id": user_id}
