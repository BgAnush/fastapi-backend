from fastapi import APIRouter, HTTPException
from supabase import create_client
import os
from datetime import datetime

router = APIRouter(prefix="/retailer")

# Supabase configuration
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

# Supabase client singleton
_supabase = None

def get_supabase():
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(
                status_code=500,
                detail="Supabase credentials not configured"
            )
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

@router.get("/test")
def retailer_test():
    """Test endpoint for retailer routes"""
    return {
        "status": "success",
        "message": "Retailer routes are working",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/produce/list")
async def get_in_stock_produce_with_farmers():
    """
    Retrieve all produce currently in stock with farmer information
    Returns:
        List of produce items with farmer details
    """
    try:
        supabase = get_supabase()

        # Fetch in-stock produce
        produce_resp = supabase.table("produce").select(
            "id,crop_name,quantity,price_per_kg,status,image_url,type,created_at,farmer_id"
        ).eq("status", "in_stock").execute()

        produce_list = produce_resp.data or []
        if not produce_list:
            return {"available_produce": []}

        # Get unique farmer IDs
        farmer_ids = list({p["farmer_id"] for p in produce_list if p.get("farmer_id")})
        
        # Fetch farmer names
        farmers_resp = supabase.table("profiles").select("id,name").in_("id", farmer_ids).execute()
        farmer_dict = {f["id"]: f["name"] for f in (farmers_resp.data or [])}

        # Format response
        result = []
        for p in produce_list:
            result.append({
                "id": p["id"],
                "crop_name": p["crop_name"],
                "type": p["type"],
                "quantity": p["quantity"],
                "price_per_kg": p["price_per_kg"],
                "status": p["status"],
                "image_url": p.get("image_url") or "https://via.placeholder.com/300x200.png?text=No+Image",
                "created_at": p["created_at"],
                "farmer_name": farmer_dict.get(p["farmer_id"], "Unknown"),
            })

        return {"available_produce": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching produce data: {str(e)}"
        )