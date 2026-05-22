from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from app.schemas import ItemCreate, ItemResponse
from app.db import get_db
from app.models import Item
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import save_db, scraper, extract_pdf, extract_voice, embed_and_store
router = APIRouter(prefix='/ingest')


@router.post("/", response_model=ItemResponse)
async def ingest(
    background_task : BackgroundTasks,
    title: str | None = Form(default=None),
    source_type: str  = Form(...),
    source_url : str | None = Form(default=None),
    content: str | None = Form(default=None),                   
    file: UploadFile | None = File(default=None),  
    db: AsyncSession = Depends(get_db),
):
    tags = ['test1']
    if source_type.lower() == 'manual':
        item = ItemCreate(
        title = title,
        content = content,
        source_type = source_type,
        source_url = source_url,
        tags = tags)

    elif source_type.lower() == 'url':
        scraped= scraper(source_url)
        content = scraped['content']
        title = title or scraped['title']
        item = ItemCreate(
            title = title,
            content = content,
            source_type = 'url',
            source_url = source_url,
            tags = tags
        )
    elif source_type.lower() == 'pdf':
        file_data = await file.read()
        extracted = extract_pdf(file_data)
        item = ItemCreate(
            title = file.filename,
            content = extracted['content'],
            source_type = 'pdf',
            tags = tags
        )
    elif source_type.lower() in ['voice', 'mp3', 'audio']:
        file_data = await file.read()
        extracted = extract_voice(file_data)
        item = ItemCreate(
            title = file.filename,
            content = extracted['content'],
            source_type = 'audio',
            tags = tags
        )
    elif source_type.lower() == 'telegram_message':
        if not content:
            raise HTTPException(status_code=400,detail='no content in telegram')
        item = ItemCreate(
            title=title,
            content = content,
            source_type = 'telegram',
            tags = tags

        )
    else:
        raise HTTPException(status_code=400, detail='Unsupported source type')
    db_item =  await save_db(item, db)
    background_task.add_task(embed_and_store,db_item.id,db_item.content, db)
    return db_item



