from fastapi import FastAPI, HTTPException, Header
from uuid import UUID
import os
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Must be service role key with delete permission

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@app.delete("/farmer/produce/{produce_id}")
async def delete_produce(produce_id: UUID, x_user_id: str = Header(...)):
    produce_id_str = str(produce_id)

    # 1. Check if produce exists and belongs to farmer with x_user_id
    response = supabase.table("produce").select("id, farmer_id").eq("id", produce_id_str).execute()

    if response.error:
        raise HTTPException(status_code=500, detail=f"Database error: {response.error.message}")

    if not response.data:
        raise HTTPException(status_code=404, detail="Produce item not found")

    produce_item = response.data[0]
    if produce_item["farmer_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this produce")

    # 2. Delete the produce item
    delete_resp = supabase.table("produce").delete().eq("id", produce_id_str).execute()

    if delete_resp.error:
        raise HTTPException(status_code=500, detail=f"Failed to delete produce: {delete_resp.error.message}")

    return {"message": "Produce item deleted successfully", "id": produce_id_str}
