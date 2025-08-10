import os
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY not set in environment variables")

router = APIRouter(
    prefix="/produce",
    tags=["Produce"]
)

class ProduceType(str, Enum):
    vegetable = "vegetable"
    fruit = "fruit"

class ProduceStatus(str, Enum):
    in_stock = "in_stock"
    out_of_stock = "out_of_stock"

class Produce(BaseModel):
    farmer_id: str = Field(..., description="UUID or identifier of the farmer")
    crop_name: str
    quantity: int
    price_per_kg: float
    image_url: Optional[str] = None
    type: ProduceType
    status: ProduceStatus = ProduceStatus.in_stock

@router.post("/add_produce")
async def add_produce(produce: Produce):
    url = f"{SUPABASE_URL}/rest/v1/produce"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",  # to get the inserted row back
    }
    data = {
        "farmer_id": produce.farmer_id,
        "crop_name": produce.crop_name,
        "quantity": produce.quantity,
        "price_per_kg": produce.price_per_kg,
        "image_url": produce.image_url,
        "type": produce.type.value,
        "status": produce.status.value,
        "created_at": "now()"  # Supabase/Postgres will interpret NOW() function
    }
    # Remove created_at as a string, we will let DB fill it by default (recommended)
    data.pop("created_at")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        if response.status_code == 201:
            inserted = response.json()
            # inserted is a list of rows, take first inserted
            return {"message": "Produce added successfully", "produce": inserted[0]}
        elif response.status_code == 409:
            # Conflict error (like foreign key violation)
            raise HTTPException(status_code=400, detail="Invalid farmer_id (foreign key violation or conflict)")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to add produce: {response.text}")
