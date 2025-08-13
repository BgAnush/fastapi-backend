from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import get_db_session  # your DB session dependency
from models import Retailer, Produce, Farmer  # your ORM models

router = APIRouter()

class ProduceItem(BaseModel):
    id: int
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
def get_retailer_dashboard(user_id: int, email: str, db=Depends(get_db_session)):
    # Fetch retailer info
    retailer = db.query(Retailer).filter(
        (Retailer.id == user_id) | (Retailer.email == email)
    ).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")

    # Fetch produce with farmer info
    produce_list = (
        db.query(Produce, Farmer)
        .join(Farmer, Produce.farmer_id == Farmer.id)
        .order_by(Produce.id.desc())
        .all()
    )

    produce_items = []
    for produce, farmer in produce_list:
        produce_items.append(
            ProduceItem(
                id=produce.id,
                crop_name=produce.crop_name,
                price_per_kg=produce.price_per_kg,
                quantity=produce.quantity,
                status=produce.status,
                image_url=produce.image_url,
                farmer_name=farmer.name,
            )
        )

    return RetailerDashboardResponse(
        retailer_name=retailer.name,
        produce=produce_items
    )
