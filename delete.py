from fastapi import APIRouter, HTTPException, status
from uuid import UUID
import traceback

import supabase

router = APIRouter()

@router.delete("/produce/delete/{produce_id}", status_code=status.HTTP_200_OK)
async def delete_produce(produce_id: UUID):
    try:
        # Your existing supabase queries here
        response = supabase.table("produce").select("id").eq("id", str(produce_id)).execute()
        if response.error:
            raise HTTPException(status_code=500, detail="Database error during lookup")
        if not response.data:
            raise HTTPException(status_code=404, detail="Produce item not found")

        delete_resp = supabase.table("produce").delete().eq("id", str(produce_id)).execute()
        if delete_resp.error:
            raise HTTPException(status_code=500, detail="Failed to delete produce item")

        return {"message": "Produce item deleted successfully", "id": str(produce_id)}

    except Exception as e:
        print(f"Exception in delete_produce: {e}")
        traceback.print_exc()   # This will print full stack trace in logs
        raise HTTPException(status_code=500, detail="Internal Server Error")