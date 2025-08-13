from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os

router = APIRouter()

SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/dashboard")
async def retailer_dashboard(request: Request):
    """
    Returns retailer profile info + their orders or purchased produce list.
    Expected JSON: { "id": "<retailer_id>" }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    retailer_id = data.get("id")
    if not retailer_id:
        raise HTTPException(status_code=400, detail="Retailer ID is required.")

    profile_resp = supabase.table("profiles").select("id,name").eq("id", retailer_id).execute()
    if getattr(profile_resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching profile.")

    if not profile_resp.data:
        raise HTTPException(status_code=404, detail="Profile not found.")

    retailer = profile_resp.data[0]

    produce_resp = (
        supabase.table("orders")
        .select("id,produce_id,quantity,total_price,status,created_at")
        .eq("retailer_id", retailer_id)
        .execute()
    )

    if getattr(produce_resp, "error", None):
        raise HTTPException(status_code=500, detail="Error fetching orders.")

    orders_data = produce_resp.data or []

    return {
        "retailer_name": retailer["name"],
        "total_orders": len(orders_data),
        "orders": orders_data,
    }
