from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Supabase credentials not found in .env file.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(payload: LoginRequest):
    """
    Authenticate a user via Supabase Auth and fetch their profile.
    """
    try:
        # Step 1: Sign in with email & password
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })

        # Validate authentication
        if not auth_response or not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id = str(auth_response.user.id)

        # Step 2: Fetch matching profile from `public.profiles`
        profile_response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()

        if profile_response.error:
            raise HTTPException(status_code=500, detail=f"Database error: {profile_response.error.message}")

        if not profile_response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Step 3: Return consistent JSON format
        return {
            "message": "✅ Login successful",
            "access_token": auth_response.session.access_token,
            "profile": profile_response.data
        }

    except HTTPException:
        # Pass through handled exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
