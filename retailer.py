from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create Retailer router with prefix
router = APIRouter(prefix="/retailer", tags=["Retailer"])

@router.get("/produce")
def get_available_produce():
    """
    Get all available produce along with farmer details.
    """
    try:
        print("🔄 Fetching available produce for retailers...")
        response = supabase.rpc("get_available_produce_with_farmer").execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No available produce found.")

        print("✅ Produce fetched successfully!")
        return {"produce": response.data}

    except Exception as e:
        print("❌ Error fetching produce:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
