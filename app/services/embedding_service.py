

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_mistralai import MistralAIEmbeddings
from sqlalchemy import select
from app.models import Item
from app.core import settings
import os


os.environ['MISTRAL_API_KEY'] = settings.mistral_api_key
embeddings = MistralAIEmbeddings(model='mistral-embed')

async def embed_and_store(item_id: int, content: str, db: AsyncSession):
    vector = embeddings.embed_query(content)
    item_db = await db.execute(select(Item).where(Item.id == item_id))
    item_detail = item_db.scalars().first()
    if item_detail:
        item_detail.embedding = vector
        item_detail.processed = True
        await db.commit()
        await db.refresh(item_detail)
    else:
        raise HTTPException(status_code = 400, detail='No Item Found')

