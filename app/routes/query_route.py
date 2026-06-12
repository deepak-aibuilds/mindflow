from fastapi import APIRouter, Depends, Query
from app.schemas import ChunkResult, ItemResponse
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import search_items, ask_brain
from pydantic import BaseModel
from app.services import generate_digest, get_action, get_cache, set_cache, delete_cache
from app.schemas import DigestOutput, ActionItems
from sqlalchemy import select
from app.models import Item
from fastapi.responses import StreamingResponse
import json

router = APIRouter(tags=['Query'])


# ── Critical Fix: question comes from JSON body, not URL param ──
# /ask?question=hello is wrong REST design for POST
# POST body is the correct pattern for sending data
class AskRequest(BaseModel):
    question: str


@router.get('/search', response_model=list[ChunkResult])
async def search_query(
    q:     str,
    limit: int          = Query(default=5, le=20),
    db:    AsyncSession = Depends(get_db),
):
    return await search_items(q, limit, db)


@router.post('/ask')
async def ask_llm(
    request: AskRequest,
    db:      AsyncSession = Depends(get_db),
):
    return StreamingResponse(ask_brain(request.question, db),media_type='text/event-stream')

@router.get('/digest', response_model=DigestOutput)
async def digest(db:AsyncSession = Depends(get_db)):
    response = await generate_digest(db)
    return response

@router.post('/actions', response_model=ActionItems)
async def get_actions(db:AsyncSession = Depends(get_db)):
    response = await get_action(db)
    return response

@router.get('/items', response_model = list[ItemResponse])
async def get_items(
    source_type: str | None  = Query(default=None),
    processed:   bool | None = Query(default=None),
    search:      str | None  = Query(default=None),
    page:        int         = Query(default=1, ge=1),
    limit:       int         = Query(default=10, le=50)   ,     
    db:AsyncSession = Depends(get_db)):
    cache_key = f"items:{source_type}:{processed}:{search}:{page}:{limit}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    
    offset_num = 0
    query = select(Item)
    if source_type:
        query = query.where(Item.source_type == source_type)
    if processed:
        query = query.where(Item.processed == processed)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))
    offset_num = (page - 1 )*limit
    query = query.offset(offset_num).limit(limit)
    result = await db.execute(query)
    result_all = result.scalars().all()
    data = [ItemResponse.model_validate(item).model_dump(mode="json") for item in result_all]
    await set_cache(cache_key, json.dumps(data), ttl=60)
    return data