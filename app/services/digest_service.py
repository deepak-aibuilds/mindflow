from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Item
from datetime import datetime, timedelta
from app.llm import get_digest



async def generate_digest(db: AsyncSession) -> str:
    last_24hrs = datetime.now() - timedelta(hours=24)
    context = await db.execute(select(Item).where(Item.created_at >= last_24hrs))
    context_all = context.scalars().all()
    if not context_all:
        context_str = 'No Context Available. So Please return just No digest message'
    else:
        context_str = '\n\n'.join([item.content for item in context_all])
    chain = get_digest()
    response = await chain.ainvoke({
        'context': context_str,
        'today': datetime.now()
    })
    return {'subject': response.subject,
            'body': response.body}



