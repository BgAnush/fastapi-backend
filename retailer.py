from fastapi import APIRouter, HTTPException
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

@router.get("/produce")
async def get_available_produce():
    try:
        # Fetch produce with status='in_stock'
        produce_resp = supabase.table("produce").select("*").eq("status", "in_stock").execute()
        if produce_resp.error:
            raise HTTPException(status_code=500, detail=f"Supabase error: {produce_resp.error.message}")

        produce_list = produce_resp.data

        if not produce_list:
            return []

        # Extract unique farmer IDs from produce
        farmer_ids = list({item["farmer_id"] for item in produce_list})

        # Fetch farmer profiles for those IDs
        profiles_resp = supabase.table("profiles").select("id, name").in_("id", farmer_ids).execute()
        if profiles_resp.error:
            raise HTTPException(status_code=500, detail=f"Supabase error: {profiles_resp.error.message}")

        profiles = profiles_resp.data

        # Map farmer id to farmer name
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        # Attach farmer_name to each produce item
        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item["farmer_id"], "Unknown")

        return produce_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
