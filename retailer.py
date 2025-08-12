from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
import os
import asyncio
from typing import List, Dict, Any

# Initialize router with prefix (choose ONE of these options)
# Option 1: With prefix (then don't add prefix in main.py)
router = APIRouter(prefix="/retailer", tags=["retailer"])

# Option 2: Without prefix (then add prefix in main.py)
# router = APIRouter(tags=["retailer"])

# Load Supabase credentials
SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/produce", response_model=List[Dict[str, Any]])
async def get_all_instock_produce():
    """Get all produce items currently in stock with farmer details."""
    try:
        # Fetch all produce items with status = 'in_stock'
        produce_resp = await supabase.table("produce") \
            .select("*") \
            .eq("status", "in_stock") \
            .execute()

        if produce_resp.error:
            raise HTTPException(
                status_code=500, 
                detail=f"Supabase error: {produce_resp.error.message}"
            )

        produce_list = produce_resp.data or []

        if not produce_list:
            return []

        # Get unique farmer IDs
        farmer_ids = list({item["farmer_id"] for item in produce_list if item.get("farmer_id")})

        if not farmer_ids:
            # If no farmer IDs, return produce with unknown farmers
            return [{"farmer_name": "Unknown", **item} for item in produce_list]

        # Fetch farmer profiles
        profiles_resp = await supabase.table("profiles") \
            .select("id, name") \
            .in_("id", farmer_ids) \
            .execute()

        if profiles_resp.error:
            raise HTTPException(
                status_code=500, 
                detail=f"Supabase error: {profiles_resp.error.message}"
            )

        profiles = profiles_resp.data or []
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        # Enhance produce items with farmer names
        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item.get("farmer_id"), "Unknown")

        return produce_list

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Server error: {str(e)}"
        )