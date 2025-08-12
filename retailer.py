from fastapi import APIRouter

router = APIRouter()

@router.post("/test")
async def test_route():
    return {"message": "Test route works"}
