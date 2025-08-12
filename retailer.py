# retailer.py
from fastapi import APIRouter, HTTPException
from supabase import create_client
import os

router = APIRouter(tags=["retailer"])

# ✅ Supabase setup
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/produce")
async def get_all_instock_produce():
    """
    Returns all produce items currently in stock with farmer names (grouped format).
    """
    # ✅ Fetch all produce in stock
    produce_resp = (
        supabase.table("produce")
        .select("id,crop_name,quantity,price_per_kg,status,image_url,type,created_at,farmer_id")
        .eq("status", "in_stock")
        .execute()
    )

    if getattr(produce_resp, "error", None):
        print(f"❌ Supabase error (produce): {produce_resp.error}")
        raise HTTPException(status_code=500, detail="Database error while fetching produce.")

    produce_list = produce_resp.data or []
    if not produce_list:
        return {"total_in_stock": 0, "produce": []}

    # ✅ Extract farmer IDs
    farmer_ids = list({item["farmer_id"] for item in produce_list if item.get("farmer_id")})
    farmer_map = {}

    if farmer_ids:
        # ✅ Fetch farmer names
        profiles_resp = (
            supabase.table("profiles")
            .select("id,name")
            .in_("id", farmer_ids)
            .execute()
        )

        if getattr(profiles_resp, "error", None):
            print(f"❌ Supabase error (profiles): {profiles_resp.error}")
            raise HTTPException(status_code=500, detail="Database error while fetching profiles.")

        profiles = profiles_resp.data or []
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

    # ✅ Attach farmer names to produce
    for item in produce_list:
        item["farmer_name"] = farmer_map.get(item.get("farmer_id"), "Unknown")

    print(f"✅ Returning {len(produce_list)} crops in stock.")
    return {
        "total_in_stock": len(produce_list),
        "produce": produce_list
    }
