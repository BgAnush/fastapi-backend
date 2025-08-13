import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from supabase import create_client, Client
from uuid import UUID

router = APIRouter()

SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ProduceItem(BaseModel):
    id: UUID
    crop_name: str
    price_per_kg: float
    quantity: int
    status: str
    image_url: Optional[str]
    farmer_name: Optional[str]

class RetailerDashboardResponse(BaseModel):
    retailer_name: str
    produce: List[ProduceItem]

@router.post("/retailer/dashboard", response_model=RetailerDashboardResponse)
def get_retailer_dashboard(user_id: UUID, email: str):
    # Fetch retailer profile
    retailer_resp = supabase.table("profiles") \
        .select("name") \
        .eq("id", str(user_id)) \
        .eq("email", email) \
        .eq("role", "retailer") \
        .execute()

    if retailer_resp.error or len(retailer_resp.data) == 0:
        raise HTTPException(status_code=404, detail="Retailer not found")

    retailer_name = retailer_resp.data[0]["name"]

    # Fetch produce with farmer details (join profiles table as farmer)
    # Supabase doesn't support joins directly; do via RPC or multiple queries.

    # Simplest way: fetch produce with farmer_id, then fetch farmers separately
    produce_resp = supabase.table("produce") \
        .select("id, crop_name, price_per_kg, quantity, status, image_url, farmer_id") \
        .order("created_at", desc=True) \
        .execute()

    if produce_resp.error:
        raise HTTPException(status_code=500, detail="Failed to fetch produce")

    produce_data = produce_resp.data

    # Get unique farmer_ids
    farmer_ids = list({item["farmer_id"] for item in produce_data})

    farmers_resp = supabase.table("profiles") \
        .select("id, name") \
        .in_("id", farmer_ids) \
        .execute()

    if farmers_resp.error:
        raise HTTPException(status_code=500, detail="Failed to fetch farmers")

    farmers_map = {farmer["id"]: farmer["name"] for farmer in farmers_resp.data}

    produce_items = []
    for item in produce_data:
        produce_items.append(
            ProduceItem(
                id=item["id"],
                crop_name=item["crop_name"],
                price_per_kg=float(item["price_per_kg"]),
                quantity=item["quantity"],
                status=item["status"],
                image_url=item.get("image_url"),
                farmer_name=farmers_map.get(item["farmer_id"], "Unknown"),
            )
        )

    return RetailerDashboardResponse(
        retailer_name=retailer_name,
        produce=produce_items
    )
