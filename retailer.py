from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create FastAPI app
app = FastAPI()


@app.get("/produce")
def get_available_produce():
    try:
        print("🔄 Fetching available produce from Supabase...")
        response = supabase.rpc("get_available_produce_with_farmer").execute()
        print("✅ Data fetched successfully!")

        if not response.data:
            raise HTTPException(status_code=404, detail="No available produce found.")

        # Return as JSON
        return {"available_produce": response.data}

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
