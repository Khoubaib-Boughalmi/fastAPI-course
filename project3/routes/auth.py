from fastapi.routing import APIRouter 

router = APIRouter()


@router.get("/auth")
async def get_user():
    return {"authorization": "user"}