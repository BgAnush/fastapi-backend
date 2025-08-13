from fastapi import APIRouter, HTTPException
from supabase import create_client
import os

router = APIRouter()

# Supabase setup from environment variables
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# This is the endpoint that the frontend is trying to call
@router.get("/produce/list")
async def get_all_produce():
    """
    Returns a list of all available produce that is in stock.
    """
    try:
        # Fetch all produce that is 'in_stock'
        produce_resp = supabase.table("produce").select("id, crop_name, quantity, price_per_kg, status, image_url, type, created_at, farmer_id").eq("status", "in_stock").execute()

        if getattr(produce_resp, "error", None):
            print(f"❌ Supabase error (produce): {produce_resp.error}")
            raise HTTPException(status_code=500, detail="Database error while fetching produce.")

        produce_data = produce_resp.data or []
        print(f"✅ Found {len(produce_data)} available crops for retailer")

        return {
            "available_produce": produce_data,
        }

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/produce/{crop_id}")
async def get_crop_details(crop_id: str):
    """
    Returns details for a single crop by its ID, including farmer name.
    """
    try:
        # Fetch crop details
        produce_resp = supabase.table("produce").select("id, crop_name, quantity, price_per_kg, status, image_url, type, created_at, farmer_id").eq("id", crop_id).single().execute()

        if getattr(produce_resp, "error", None):
            if produce_resp.error.get("code") == "PGRST116":  # Not Found error
                raise HTTPException(status_code=404, detail="Crop not found.")
            print(f"❌ Supabase error (crop details): {produce_resp.error}")
            raise HTTPException(status_code=500, detail="Database error while fetching crop details.")
        
        crop_data = produce_resp.data

        # Fetch farmer details
        farmer_resp = supabase.table("profiles").select("name").eq("id", crop_data["farmer_id"]).single().execute()

        if getattr(farmer_resp, "error", None):
             print(f"❌ Supabase error (farmer details): {farmer_resp.error}")
             # We can still return the crop data even if the farmer name isn't found
             farmer_name = "Unknown Farmer"
        else:
            farmer_name = farmer_resp.data["name"]
        
        crop_data["farmer_name"] = farmer_name

        return crop_data

    except HTTPException:
        raise # re-raise the HTTPException
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")