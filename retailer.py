# retailer.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix="/retailer", tags=["Retailer"])


# ---------- MODELS ----------
class ProduceItem(BaseModel):
    id: str
    crop_name: str
    quantity: int
    price_per_kg: float
    status: str
    image_url: str | None
    type: str
    created_at: str
    farmer_id: str
    farmer_name: str
    farmer_email: str


class AddToCartRequest(BaseModel):
    retailer_id: str
    crop_id: str
    quantity: int


# ---------- ROUTES ----------
@router.get("/dashboard")
def retailer_dashboard():
    try:
        response = supabase.rpc("get_available_produce_with_farmer").execute()
        if response.error:
            raise HTTPException(status_code=500, detail=response.error.message)
        return {"produce": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {e}")



@router.post("/add-to-cart")
def add_to_cart(payload: AddToCartRequest):
    """
    Add a produce item to the retailer's cart.
    If item already exists in cart for this retailer, increase the quantity.
    """
    try:
        # Validate crop exists and has enough stock
        crop = supabase.table("produce").select("quantity").eq("id", payload.crop_id).gte("quantity", payload.quantity).execute()
        if not crop.data:
            raise HTTPException(status_code=400, detail="Invalid crop or insufficient stock")

        # Check if already in cart
        existing = supabase.table("cart").select("id", "quantity").eq("retailer_id", payload.retailer_id).eq("crop_id", payload.crop_id).execute()

        if existing.data:
            cart_id = existing.data[0]["id"]
            new_quantity = existing.data[0]["quantity"] + payload.quantity
            supabase.table("cart").update({"quantity": new_quantity}).eq("id", cart_id).execute()
        else:
            supabase.table("cart").insert({
                "retailer_id": payload.retailer_id,
                "crop_id": payload.crop_id,
                "quantity": payload.quantity
            }).execute()

        return {"message": "Item added to cart successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to cart: {e}")
