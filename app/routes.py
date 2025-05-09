
from fastapi import APIRouter, HTTPException
from models.idea import Idea

router = APIRouter()

@router.get("/ideas", response_model=list[Idea])
async def get_ideas():
    return []

@router.get("/ideas/{source}", response_model=list[Idea])
async def get_ideas_by_source(source: str):
    return []
