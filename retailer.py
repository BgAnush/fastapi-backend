from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
import os
import asyncio

router = APIRouter()

SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/produce")
async def get_all_instock_produce():
    try:
        # Supabase python client is synchronous, but you can run in a thread or async wrapper if needed.
        # If your client is async, use `await`. Here, assuming sync, use run_in_executor:
        loop = asyncio.get_event_loop()

        produce_resp = await loop.run_in_executor(
            None,
            lambda: supabase.table("produce").select("*").eq("status", "in_stock").execute()
        )

        if produce_resp.error:
            raise HTTPException(status_code=500, detail=f"Supabase error: {produce_resp.error.message}")

        produce_list = produce_resp.data or []

        if not produce_list:
            return []

        farmer_ids = list({item["farmer_id"] for item in produce_list})

        profiles_resp = await loop.run_in_executor(
            None,
            lambda: supabase.table("profiles").select("id, name").in_("id", farmer_ids).execute()
        )

        if profiles_resp.error:
            raise HTTPException(status_code=500, detail=f"Supabase error: {profiles_resp.error.message}")

        profiles = profiles_resp.data or []

        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item["farmer_id"], "Unknown")

        return produce_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
