from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
import os
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

# Supabase setup
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class RetailerDashboardResponse(BaseModel):
    retailer_name: str
    available_produce: List[dict]
    total_negotiations: int
    unread_messages: int

@router.post("/dashboard", response_model=RetailerDashboardResponse)
async def retailer_dashboard(request: Request):
    """
    Returns retailer profile info + available produce list + negotiation stats.
    Expected JSON: { "user_id": "<retailer_id>", "email": "<retailer_email>" }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    retailer_id = data.get("user_id")
    email = data.get("email")
    
    if not retailer_id or not email:
        raise HTTPException(
            status_code=400,
            detail="Both user_id and email are required."
        )

    print(f"📩 Received retailer dashboard request: retailer_id={retailer_id}")

    try:
        # Fetch retailer profile
        profile_resp = supabase.table("profiles").select("id,name").eq("id", retailer_id).execute()
        if profile_resp.error:
            print(f"❌ Supabase error (profiles): {profile_resp.error}")
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching profile."
            )

        if not profile_resp.data:
            raise HTTPException(
                status_code=404,
                detail="Retailer profile not found."
            )

        retailer = profile_resp.data[0]
        retailer_name = retailer["name"]

        # Fetch all available produce (quantity > 0)
        produce_resp = supabase.rpc(
            "get_available_produce_with_farmer",
            {}
        ).execute()

        if produce_resp.error:
            print(f"❌ Supabase error (produce): {produce_resp.error}")
            raise HTTPException(
                status_code=500,
                detail="Database error while fetching produce."
            )

        available_produce = produce_resp.data or []

        # Count active negotiations for this retailer
        negotiations_resp = supabase.table("negotiations") \
            .select("id", count="exact") \
            .eq("retailer_id", retailer_id) \
            .neq("status", "completed") \
            .execute()

        total_negotiations = negotiations_resp.count or 0

        # Count unread messages (placeholder - implement your messaging system)
        unread_messages = 0  # Replace with actual query

        print(f"✅ Found {len(available_produce)} available crops for retailer '{retailer_name}'")

        return {
            "retailer_name": retailer_name,
            "available_produce": available_produce,
            "total_negotiations": total_negotiations,
            "unread_messages": unread_messages,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        )
