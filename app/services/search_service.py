from sqlalchemy.ext.asyncio import AsyncSession
from .embedding_service import embeddings
from sqlalchemy import select
from app.models import Item, Chunk
from app.core import logger, settings
import cohere
from rank_bm25 import BM25Okapi


co = cohere.Client(api_key = settings.cohere_api_key)


async def search_items(query: str, limit: int, db: AsyncSession) -> list:
    try:
        query_vector = embeddings.embed_query(query)
    except Exception as e:
        logger.error("Failed to embed search query", extra={"error": str(e)})
        return []

    results = await db.execute(
        select(Chunk)
        .where(Chunk.embedding.is_not(None))  
        .order_by(Chunk.embedding.cosine_distance(query_vector))
        .limit(10)
    )
    chunks = results.scalars().all()
    corpus = [chunk.content.split() for chunk in chunks]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query.split())
    vector_ranks = {chunk.id: i for i, chunk in enumerate(chunks)}
    bm25_ranks = {
    chunk.id: rank 
    for rank, (score, chunk) in enumerate(
        sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    )
}
    rrf_scores = {
    chunk.id: 1/(vector_ranks[chunk.id] + 60) + 1/(bm25_ranks[chunk.id] + 60)
        for chunk in chunks
    }
    chunks = sorted(chunks, key=lambda c: rrf_scores[c.id], reverse=True)[:limit*2]
    result_chunks = co.rerank(
        query=query,
        documents=[chunk.content for chunk in chunks],
        top_n = limit,
        model='rerank-english-v3.0'

    )
    reranked = [chunks[r.index] for r in result_chunks.results]
    item_ids = list(set([chunk.item_id for chunk in reranked]))
    item_result = await db.execute(select(Item).where(Item.id.in_(item_ids)))
    item_map = {item.id:item for item in item_result.scalars().all()}
    chunk_result = []
    for chunk in reranked:
        parent_item = item_map[chunk.item_id]
        chunk_result.append({
            'chunk_content': chunk.content,
            'item_title': parent_item.title,
            'source_type': parent_item.source_type,
            'item_id': chunk.item_id
        })
    return chunk_result