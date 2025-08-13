from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os

router = APIRouter()

# ✅ Supabase setup from environment variables
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/dashboard")
async def farmer_dashboard(request: Request):
    """
    Returns farmer profile info + their produce list.
    Expected JSON: { "id": "<farmer_id>" }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    farmer_id = data.get("id")
    print(f"📩 Received dashboard request: farmer_id={farmer_id}")

    if not farmer_id:
        raise HTTPException(status_code=400, detail="Farmer ID is required.")

    # ✅ Fetch farmer profile
    profile_resp = supabase.table("profiles").select("id,name").eq("id", farmer_id).execute()
    if getattr(profile_resp, "error", None):
        print(f"❌ Supabase error (profiles): {profile_resp.error}")
        raise HTTPException(status_code=500, detail="Database error while fetching profile.")

    if not profile_resp.data:
        raise HTTPException(status_code=404, detail="Profile not found.")

    farmer = profile_resp.data[0]
    farmer_name = farmer["name"]

    # ✅ Fetch farmer's produce
    produce_resp = (
        supabase.table("produce")
        .select("id,crop_name,quantity,price_per_kg,status,image_url,type,created_at")
        .eq("farmer_id", farmer_id)
        .execute()
    )

    if getattr(produce_resp, "error", None):
        print(f"❌ Supabase error (produce): {produce_resp.error}")
        raise HTTPException(status_code=500, detail="Database error while fetching produce.")

    produce_data = produce_resp.data or []
    print(f"✅ Found {len(produce_data)} crops for farmer '{farmer_name}'")

    return {
        "farmer_name": farmer_name,
        "total_crops": len(produce_data),
        "produce": produce_data,
    }
