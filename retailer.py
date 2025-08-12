from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("EXPO_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_instock_produce():
    try:
        produce_resp = supabase.table("produce").select("*").eq("status", "in_stock").execute()
        if getattr(produce_resp, "error", None):
            print(f"Supabase error: {produce_resp.error.message}")
            return None

        produce_list = produce_resp.data or []
        if not produce_list:
            print("No produce found with status 'in_stock'.")
            return []

        farmer_ids = list({item["farmer_id"] for item in produce_list})

        profiles_resp = supabase.table("profiles").select("id, name").in_("id", farmer_ids).execute()
        if getattr(profiles_resp, "error", None):
            print(f"Supabase error: {profiles_resp.error.message}")
            return None

        profiles = profiles_resp.data or []
        farmer_map = {profile["id"]: profile["name"] for profile in profiles}

        for item in produce_list:
            item["farmer_name"] = farmer_map.get(item["farmer_id"], "Unknown")

        return produce_list

    except Exception as e:
        print(f"Database error: {str(e)}")
        return None


if __name__ == "__main__":
    produce = get_all_instock_produce()
    if produce is None:
        print("Failed to fetch produce.")
    else:
        unique_ids = set(item['id'] for item in produce)
        print(f"Found {len(produce)} produce items ({len(unique_ids)} unique):\n")
        print(json.dumps(produce, indent=2))
