from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os

router = APIRouter()

# Supabase setup from environment variables
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/dashboard")  # This combined with prefix makes /retailer/dashboard
async def retailer_dashboard(request: Request):
    # Your implementation here
    return {"message": "This is the retailer dashboard"}
    """
    Returns retailer profile info + available produce list with farmer names.
    Expected JSON: { "id": "<retailer_id>" }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    retailer_id = data.get("id")
    print(f"📩 Received retailer dashboard request: retailer_id={retailer_id}")

    if not retailer_id:
        raise HTTPException(status_code=400, detail="Retailer ID is required.")

    # ✅ Fetch retailer profile
    profile_resp = supabase.table("profiles").select("id,name").eq("id", retailer_id).execute()
    if getattr(profile_resp, "error", None):
        print(f"❌ Supabase error (profiles): {profile_resp.error}")
        raise HTTPException(status_code=500, detail="Database error while fetching profile.")

    if not profile_resp.data:
        raise HTTPException(status_code=404, detail="Profile not found.")

    retailer = profile_resp.data[0]
    retailer_name = retailer["name"]

    # ✅ Fetch available produce with farmer names
    # This query joins the produce table with the profiles table to get farmer names
    produce_resp = (
        supabase.table("produce")
        .select("""
            id,
            crop_name,
            quantity,
            price_per_kg,
            status,
            image_url,
            type,
            created_at,
            farmer_id,
            profiles:farmer_id(name)
        """)
        .neq("quantity", 0)  # Only show produce with quantity > 0
        .order("created_at", desc=True)
        .execute()
    )

    if getattr(produce_resp, "error", None):
        print(f"❌ Supabase error (produce): {produce_resp.error}")
        raise HTTPException(status_code=500, detail="Database error while fetching produce.")

    # Process the data to flatten the farmer name
    produce_data = []
    for item in produce_resp.data or []:
        farmer_info = item.get("profiles", {})
        produce_data.append({
            "id": item["id"],
            "crop_name": item["crop_name"],
            "quantity": item["quantity"],
            "price_per_kg": item["price_per_kg"],
            "status": item["status"],
            "image_url": item["image_url"],
            "type": item["type"],
            "created_at": item["created_at"],
            "farmer_id": item["farmer_id"],
            "farmer_name": farmer_info.get("name", "Unknown Farmer"),
        })

    print(f"✅ Found {len(produce_data)} available crops for retailer '{retailer_name}'")

    return {
        "retailer_name": retailer_name,
        "total_available": len(produce_data),
        "produce": produce_data,
    }