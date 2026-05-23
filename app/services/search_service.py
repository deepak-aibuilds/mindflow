from sqlalchemy.ext.asyncio import AsyncSession
from .embedding_service import embeddings
from sqlalchemy import select
from app.models import Item
from app.core import logger


async def search_items(query: str, limit: int, db: AsyncSession) -> list:
    try:
        query_vector = embeddings.embed_query(query)
    except Exception as e:
        logger.error("Failed to embed search query", extra={"error": str(e)})
        return []

    # ── Critical Fix: Only search items that have been embedded ──
    # Items with embedding=NULL (processed=False) will cause a
    # cosine_distance error. Filter to processed=True only.
    results = await db.execute(
        select(Item)
        .where(Item.processed == True)       # noqa: E712 — SQLAlchemy needs ==
        .where(Item.embedding.is_not(None))  # extra safety — skip NULL embeddings
        .order_by(Item.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    return results.scalars().all()