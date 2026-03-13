from fastapi import APIRouter
from models.store import store

router = APIRouter()

@router.get("/stats")
def get_stats():
    return store.get_stats()
