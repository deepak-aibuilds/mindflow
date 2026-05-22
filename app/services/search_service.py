from sqlalchemy.ext.asyncio import AsyncSession
from .embedding_service import embeddings
from pgvector.sqlalchemy import Vector
from sqlalchemy import select, func
from app.models import Item


async def search_items(query:str,limit:int, db:AsyncSession) -> list:
    query_vector = embeddings.embed_query(query)
    results = await db.execute(
    select(Item)
    .order_by(Item.embedding.cosine_distance(query_vector))
    .limit(limit)
)
    return results.scalars().all()
