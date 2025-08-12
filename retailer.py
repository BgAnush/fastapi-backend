from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os
from pydantic import BaseModel

router = APIRouter()

# Supabase setup
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Request model
class RetailerRequest(BaseModel):
    id: str
    # email: str  # Uncomment if needed

@router.post("/dashboard")
async def retailer_dashboard(request: RetailerRequest):
    """
    Returns retailer profile and available produce
    Test with Postman using:
    POST /retailer/dashboard
    Body (JSON): {"id": "your_retailer_id"}
    """
    try:
        # Get retailer profile
        profile_resp = supabase.table("profiles") \
            .select("id,name") \
            .eq("id", request.id) \
            .execute()

        if profile_resp.error:
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching profile"
            )

        if not profile_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        retailer = profile_resp.data[0]
        
        # Get available produce with farmer names
        produce_resp = supabase.table("produce") \
            .select("""
                id, crop_name, quantity, price_per_kg,
                status, image_url, type, created_at,
                farmer_id, profiles:farmer_id(name)
            """) \
            .neq("quantity", 0) \
            .order("created_at", desc=True) \
            .execute()

        if produce_resp.error:
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching produce"
            )

        # Format response
        produce_data = []
        for item in produce_resp.data or []:
            farmer_info = item.get("profiles", {})
            produce_data.append({
                "id": item["id"],
                "crop_name": item["crop_name"],
                "price": item["price_per_kg"],
                "quantity": item["quantity"],
                "status": item["status"],
                "image_url": item["image_url"],
                "farmer_name": farmer_info.get("name", "Unknown Farmer"),
                "farmer_id": item["farmer_id"]
            })

        return {
            "retailer_name": retailer["name"],
            "produce": produce_data,
            "count": len(produce_data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )