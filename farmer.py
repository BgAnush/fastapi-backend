from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os

router = APIRouter()

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/dashboard")
async def farmer_dashboard(request: Request):
    data = await request.json()
    farmer_id = data.get("id")

    print(f"📩 Dashboard request: farmer_id={farmer_id}")

    if not farmer_id:
        raise HTTPException(status_code=400, detail="Farmer ID is required")

    # Fetch farmer profile by ID
    profile_resp = supabase.table("profiles").select("id,name").eq("id", farmer_id).execute()

    if not profile_resp.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    farmer = profile_resp.data[0]
    farmer_name = farmer["name"]

    # Fetch produce by farmer_id
    produce_resp = (
        supabase.table("produce")
        .select("id,crop_name,quantity,price_per_kg,status,image_url,type,created_at")
        .eq("farmer_id", farmer_id)
        .execute()
    )

    produce_data = produce_resp.data or []
    print(f"✅ Found {len(produce_data)} crops for farmer '{farmer_name}'")

    return {
        "farmer_name": farmer_name,
        "total_crops": len(produce_data),
        "produce": produce_data,
    }
