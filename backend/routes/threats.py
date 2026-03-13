from fastapi import APIRouter
from models.store import store

router = APIRouter()

@router.get("/threats")
def get_threats(limit: int = 50):
    return {"threats": [t.model_dump() for t in store.get_all(limit)]}
