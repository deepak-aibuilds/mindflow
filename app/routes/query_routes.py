from fastapi import APIRouter, Depends,Query, HTTPException, BackgroundTasks
from app.schemas import ItemCreate, ItemResponse
from app.db import get_db
from app.models import Item
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import search_items, ask_brain
router = APIRouter()

@router.get('/search', response_model = list[ItemResponse] )
async def search_query(
    q:str,
    limit:int = Query(default=5, le=20), 
    db: AsyncSession = Depends(get_db)
):
    similar_data = await search_items(q,limit,db)
    return similar_data

@router.post('/ask')
async def ask_llm(
    question:str,
    db:AsyncSession = Depends(get_db)
):
    response = await ask_brain(question,db)
    return response