from fastapi import APIRouter, HTTPException
from supabase import create_client
import os

router = APIRouter()

SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/produce")
async def get_all_instock_produce():
    try:
        produce_resp = supabase.table("produce").select("*").eq("status", "in_stock").execute()
        if getattr(produce_resp, "error", None):
            raise HTTPException(status_code=500, detail=f"Supabase error: {produce_resp.error.message}")

        produce_list = produce_resp.data or []
        if not produce_list:
            return []

        farmer_ids = list({item["farmer_id"] for item in produce_list})

        profiles_resp = supabase.table("profiles").select("id, name").in_("id", farmer_ids).execute()
        if getattr(profiles_resp, "error", None):
            raise HTTPException(status_code=500, detail=f"Supabase error: {profiles_resp.error.message}")

        profiles = profiles_resp.data or []
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item["farmer_id"], "Unknown")

        return produce_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
