from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os

router = APIRouter()

SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@router.post("/produce")
async def get_produce_list(request: Request):
    """
    Returns list of available produce for retailers to view.
    Expected JSON (optional): filters like crop_name, farmer_id etc.
    """

    try:
        data = await request.json()
    except Exception:
        data = {}

    crop_name = data.get("crop_name")
    status = data.get("status", "in_stock")  # default to in_stock only

    query = supabase.table("produce").select(
        "id,crop_name,quantity,price_per_kg,status,image_url,type,created_at,farmer_id"
    ).eq("status", status)

    if crop_name:
        query = query.ilike("crop_name", f"%{crop_name}%")

    produce_resp = query.execute()

    if getattr(produce_resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching produce.")

    produce_list = produce_resp.data or []

    return {"total_produce": len(produce_list), "produce": produce_list}


@router.post("/retailer/profile")
async def get_retailer_profile(request: Request):
    """
    Returns retailer profile info.
    Expected JSON: { "id": "<retailer_id>" }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    retailer_id = data.get("id")
    if not retailer_id:
        raise HTTPException(status_code=400, detail="Retailer ID required.")

    profile_resp = supabase.table("profiles").select("id,name,email").eq("id", retailer_id).execute()

    if getattr(profile_resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching profile.")

    if not profile_resp.data:
        raise HTTPException(status_code=404, detail="Profile not found.")

    retailer = profile_resp.data[0]

    return {"retailer": retailer}
