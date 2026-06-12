
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_mistralai import ChatMistralAI

from app.core import settings
from app.services import search_items
import os


os.environ['MISTRAL_API_KEY'] = settings.mistral_api_key


llm = ChatMistralAI(model='mistral-small-latest')

async def ask_brain(question:str, db:AsyncSession):
    similar_chunks = await search_items(question,3,db)
    if not similar_chunks:
        yield "I don't have anything relevant in my knowledge for this question"
        return
    context = "\n\n".join([chunk["chunk_content"] for chunk in similar_chunks])
    sources = [f"- {chunk['item_title']} ({chunk['source_type']})" for chunk in similar_chunks]
    sources_str = '\n'.join(sources)
    prompt = f"""
You are a helpful AI assistant answering questions using the provided context notes.

Instructions:
- Use ONLY the information from the context to answer.
- If the answer cannot be found in the provided context, 
respond with exactly: "I don't have this in my knowledge base."
Do not use your general knowledge. Only answer from the context provided.
- Be concise, accurate, and easy to understand.
- Do not hallucinate or make up facts.
- When useful, summarize information in bullet points.

Sources:
{sources_str}

Context:
{context}

Question:
{question}

Answer:
"""
    async for chunk in llm.astream(prompt):
        yield chunk.content


