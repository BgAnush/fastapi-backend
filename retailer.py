import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from typing import List, Optional
from supabase import create_client, Client
from uuid import UUID
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/retailer",
    tags=["retailer"],
    responses={404: {"description": "Not found"}},
)

# Initialize Supabase client with error handling
try:
    SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("EXPO_PUBLIC_SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not configured")
        
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

class ProduceItem(BaseModel):
    id: UUID4
    crop_name: str
    price_per_kg: float
    quantity: float  # Changed to float to handle decimal quantities
    status: str
    image_url: Optional[str]
    farmer_name: str
    distance_km: Optional[float] = None
    created_at: Optional[datetime] = None

class RetailerDashboardResponse(BaseModel):
    retailer_name: str
    produce: List[ProduceItem]

class RetailerDashboardRequest(BaseModel):
    user_id: UUID4
    email: str
    filters: Optional[dict] = None

async def get_retailer_profile(user_id: UUID, email: str) -> dict:
    """Fetch retailer profile with validation"""
    try:
        response = supabase.table("profiles") \
            .select("id, name, location") \
            .eq("id", str(user_id)) \
            .eq("email", email) \
            .eq("role", "retailer") \
            .maybe_single() \
            .execute()
            
        if not response.data:
            logger.warning(f"Retailer not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retailer profile not found"
            )
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching retailer profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve retailer profile"
        )

async def get_available_produce(filters: Optional[dict] = None) -> List[dict]:
    """Fetch available produce with optional filters"""
    try:
        query = supabase.table("produce") \
            .select("""
                id, 
                crop_name, 
                price_per_kg, 
                quantity, 
                status, 
                image_url, 
                farmer_id,
                location,
                created_at
            """) \
            .order("created_at", desc=True) \
            .limit(100)  # Prevent unbounded result sets
            
        # Apply status filter if provided
        if filters and filters.get("status"):
            query = query.eq("status", filters["status"])
            
        # Apply price range filter if provided
        if filters and filters.get("price_min") is not None:
            query = query.gte("price_per_kg", float(filters["price_min"]))
        if filters and filters.get("price_max") is not None:
            query = query.lte("price_per_kg", float(filters["price_max"]))
            
        response = query.execute()
        
        if response.error:
            logger.error(f"Supabase error: {response.error}")
            raise Exception(response.error.message)
            
        return response.data
    except Exception as e:
        logger.error(f"Error fetching produce: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve produce listings"
        )

async def get_farmers_details(farmer_ids: List[UUID]) -> dict:
    """Fetch farmer names in bulk"""
    if not farmer_ids:
        return {}
        
    try:
        response = supabase.table("profiles") \
            .select("id, name") \
            .in_("id", [str(id) for id in farmer_ids]) \
            .execute()
            
        if response.error:
            logger.error(f"Supabase error fetching farmers: {response.error}")
            return {}
            
        return {farmer["id"]: farmer["name"] for farmer in response.data}
    except Exception as e:
        logger.error(f"Error fetching farmers: {str(e)}")
        return {}

def calculate_distance(location1: Optional[dict], location2: Optional[dict]) -> Optional[float]:
    """Simple distance calculation (placeholder for actual geospatial calculation)"""
    if not location1 or not location2:
        return None
        
    try:
        # This is a simplified calculation - replace with proper geospatial function
        lat1 = location1.get("latitude", 0)
        lon1 = location1.get("longitude", 0)
        lat2 = location2.get("latitude", 0)
        lon2 = location2.get("longitude", 0)
        
        # Approximate calculation (Haversine would be better)
        distance = ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5 * 111  # 111km per degree
        return round(distance, 2)
    except Exception:
        return None

@router.post("/dashboard", response_model=RetailerDashboardResponse)
async def get_retailer_dashboard(request: RetailerDashboardRequest):
    """
    Retrieve dashboard data for retailer including:
    - Retailer profile information
    - Available produce listings
    - Farmer details for each listing
    """
    try:
        # 1. Validate and fetch retailer profile
        retailer = await get_retailer_profile(request.user_id, request.email)
        
        # 2. Fetch available produce with filters
        produce_data = await get_available_produce(request.filters)
        
        if not produce_data:
            return RetailerDashboardResponse(
                retailer_name=retailer["name"],
                produce=[]
            )
            
        # 3. Get farmer details in bulk
        farmer_ids = list({item["farmer_id"] for item in produce_data if item.get("farmer_id")})
        farmers_map = await get_farmers_details(farmer_ids)
        
        # 4. Transform data into response model
        produce_items = []
        for item in produce_data:
            # Calculate distance if retailer has location data
            distance = None
            if retailer.get("location") and item.get("location"):
                distance = calculate_distance(retailer["location"], item["location"])
                
            produce_items.append(
                ProduceItem(
                    id=item["id"],
                    crop_name=item["crop_name"],
                    price_per_kg=float(item["price_per_kg"]),
                    quantity=float(item["quantity"]),
                    status=item["status"],
                    image_url=item.get("image_url"),
                    farmer_name=farmers_map.get(item["farmer_id"], "Unknown Farmer"),
                    distance_km=distance,
                    created_at=item.get("created_at")
                )
            )
            
        # 5. Apply distance filter if provided
        if request.filters and request.filters.get("distance_max") is not None:
            max_distance = float(request.filters["distance_max"])
            produce_items = [item for item in produce_items 
                          if item.distance_km is None or item.distance_km <= max_distance]
            
        return RetailerDashboardResponse(
            retailer_name=retailer["name"],
            produce=produce_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in dashboard endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        )