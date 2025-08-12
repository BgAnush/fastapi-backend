from fastapi import APIRouter, HTTPException
from supabase import create_client
import os

router = APIRouter()

# Load Supabase credentials from environment variables
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/produce")
async def get_all_instock_produce():
    """
    Fetch all produce with status='in_stock' across all farmers,
    and include each farmer's name with their produce.
    """
    try:
        # Fetch all produce with status 'in_stock'
        produce_resp = supabase.table("produce").select("*").eq("status", "in_stock").execute()
        if getattr(produce_resp, "error", None):
            raise HTTPException(status_code=500, detail=f"Supabase error: {produce_resp.error.message}")

        produce_list = produce_resp.data or []
        if not produce_list:
            return []

        # Extract unique farmer IDs from produce
        farmer_ids = list({item["farmer_id"] for item in produce_list})

        # Fetch farmer profiles for those IDs (id and name)
        profiles_resp = supabase.table("profiles").select("id, name").in_("id", farmer_ids).execute()
        if getattr(profiles_resp, "error", None):
            raise HTTPException(status_code=500, detail=f"Supabase error: {profiles_resp.error.message}")

        profiles = profiles_resp.data or []

        # Map farmer_id to farmer_name
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        # Attach farmer_name to each produce item
        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item["farmer_id"], "Unknown")

        return produce_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
