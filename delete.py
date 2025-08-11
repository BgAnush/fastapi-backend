from fastapi import FastAPI, HTTPException
from uuid import UUID
import os
from supabase import create_client

app = FastAPI()

# Load your Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Must be service role key with delete permission

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

@app.delete("/produce/{produce_id}")
async def delete_produce(produce_id: UUID):
    produce_id_str = str(produce_id)

    # Check if produce exists
    response = supabase.table("produce").select("id").eq("id", produce_id_str).execute()

    if response.error:
        raise HTTPException(status_code=500, detail=f"Database error: {response.error.message}")

    if not response.data:
        raise HTTPException(status_code=404, detail="Produce item not found")

    # Delete the produce item
    delete_resp = supabase.table("produce").delete().eq("id", produce_id_str).execute()

    if delete_resp.error:
        raise HTTPException(status_code=500, detail=f"Failed to delete produce: {delete_resp.error.message}")

    return {"message": "Produce item deleted successfully", "id": produce_id_str}
