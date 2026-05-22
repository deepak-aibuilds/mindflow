
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_mistralai import ChatMistralAI

from app.core import settings
from app.services import search_items
import os


os.environ['MISTRAL_API_KEY'] = settings.mistral_api_key


llm = ChatMistralAI(model='mistral-small-latest')

async def ask_brain(question:str, db:AsyncSession):
    similar_items = await search_items(question,3,db)
    context = "\n\n".join([item.content for item in similar_items])
    prompt = f"""
You are a helpful AI assistant answering questions using the provided context notes.

Instructions:
- Use ONLY the information from the context to answer.
- If the answer is not clearly available in the context, say:
  "I could not find that information in the provided notes."
- Be concise, accurate, and easy to understand.
- Do not hallucinate or make up facts.
- When useful, summarize information in bullet points.

Context:
{context}

Question:
{question}

Answer:
"""
    response = await llm.ainvoke(prompt)
    return response.content

