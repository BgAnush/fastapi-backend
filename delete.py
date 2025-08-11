from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from supabase import create_client, Client
import os

router = APIRouter()

# Setup Supabase client (or your DB client)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.delete("/produce/delete/{produce_id}", status_code=status.HTTP_200_OK)
async def delete_produce(produce_id: UUID):
    """
    Delete a produce record by UUID.
    """
    # Check if produce exists
    response = supabase.table("produce").select("id").eq("id", str(produce_id)).execute()
    if response.error:
        raise HTTPException(status_code=500, detail="Database error during lookup")
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Produce item not found")
    
    # Perform delete
    delete_resp = supabase.table("produce").delete().eq("id", str(produce_id)).execute()
    if delete_resp.error:
        raise HTTPException(status_code=500, detail="Failed to delete produce item")

    return {"message": "Produce item deleted successfully", "id": str(produce_id)}
