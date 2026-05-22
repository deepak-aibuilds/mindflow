from app.schemas import ItemCreate
from app.models import Item

async def save_db(item: ItemCreate, db):
    db_item = Item(**item.model_dump(), processed=False)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item