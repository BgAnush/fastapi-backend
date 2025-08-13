from fastapi import APIRouter, HTTPException
from supabase import create_client
import os
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["Retailer"])

# Response Models
class ProduceItem(BaseModel):
    id: int
    crop_name: str
    type: str
    quantity: float
    price_per_kg: float
    status: str
    image_url: str
    created_at: datetime
    farmer_name: str

class ProduceListResponse(BaseModel):
    available_produce: List[ProduceItem]

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@router.get("/test", response_model=dict)
async def test_retailer():
    """Test endpoint for retailer routes"""
    return {
        "status": "success",
        "message": "Retailer routes are working",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/produce/list", response_model=ProduceListResponse)
async def get_produce_list():
    """
    Retrieve all available produce with farmer information
    Returns:
        - List of produce items with details
        - Farmer information for each item
    """
    try:
        # Fetch in-stock produce
        produce_data = supabase.table("produce")\
            .select("*, farmer:profiles(name)")\
            .eq("status", "in_stock")\
            .execute()
        
        if not produce_data.data:
            return {"available_produce": []}

        # Format response
        return {
            "available_produce": [
                {
                    "id": item["id"],
                    "crop_name": item["crop_name"],
                    "type": item["type"],
                    "quantity": item["quantity"],
                    "price_per_kg": item["price_per_kg"],
                    "status": item["status"],
                    "image_url": item.get("image_url") or "https://via.placeholder.com/300x200.png?text=No+Image",
                    "created_at": item["created_at"],
                    "farmer_name": item["farmer"]["name"] if item.get("farmer") else "Unknown"
                }
                for item in produce_data.data
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching produce data: {str(e)}"
        )