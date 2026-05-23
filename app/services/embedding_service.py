from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from langchain_mistralai import MistralAIEmbeddings
from sqlalchemy import select
from app.models import Item
from app.core import settings, logger
from app.db import engine
import os
import traceback

os.environ['MISTRAL_API_KEY'] = settings.mistral_api_key
embeddings = MistralAIEmbeddings(model='mistral-embed')

# ── Critical Fix 1: Own session factory ──────────────────────
# Background tasks CANNOT reuse the request's DB session —
# the session is closed before the background task runs.
# We create a fresh session here instead.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def embed_and_store(item_id: int, content: str):
    # ── Critical Fix 2: Own session, not passed from route ───
    async with AsyncSessionLocal() as db:
        try:
            # ── Critical Fix 3: Wrap external API call ───────
            # Mistral API can fail — network error, rate limit, etc.
            # We catch and log instead of crashing silently.
            try:
                vector = embeddings.embed_query(content)
            except Exception as e:
                logger.error(
                    "Embedding generation failed",
                    extra={"item_id": item_id, "error": str(e)}
                )
                return  # don't crash — item stays with processed=False

            result = await db.execute(select(Item).where(Item.id == item_id))
            item_detail = result.scalars().first()

            if item_detail is None:
                # ── Critical Fix 4: No HTTPException in background tasks ──
                # HTTPException only works in HTTP request context.
                # In a background task, just log and return.
                logger.error(
                    "Item not found for embedding",
                    extra={"item_id": item_id}
                )
                return

            item_detail.embedding = vector
            item_detail.processed = True
            await db.commit()
            await db.refresh(item_detail)

            logger.info(
                "Embedding stored successfully",
                extra={"item_id": item_id}
            )

        except Exception as e:
            await db.rollback()
            logger.error(
                "embed_and_store failed",
                extra={
                    "item_id": item_id, 
                    "error": str(e),
                    "traceback": traceback.format_exc()  # add this
                }
    )