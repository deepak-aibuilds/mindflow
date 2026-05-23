from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from app.schemas import ItemCreate, ItemResponse
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import save_db, scraper, extract_pdf, extract_voice, embed_and_store

router = APIRouter(prefix='/ingest', tags=['Ingest'])


@router.post("/", response_model=ItemResponse)
async def ingest(
    background_tasks: BackgroundTasks,   # fixed: plural, correct FastAPI convention
    title:       str | None    = Form(default=None),
    source_type: str           = Form(...),
    source_url:  str | None    = Form(default=None),
    content:     str | None    = Form(default=None),
    file:        UploadFile | None = File(default=None),
    db:          AsyncSession  = Depends(get_db),
):
    tags = [source_type]   # use source_type as default tag until LLM tagging is built

    if source_type.lower() == 'manual':
        if not content:
            raise HTTPException(status_code=400, detail="Content is required for manual ingestion")
        item = ItemCreate(
            title=title,
            content=content,
            source_type=source_type,
            source_url=source_url,
            tags=tags,
        )

    elif source_type.lower() == 'url':
        if not source_url:
            raise HTTPException(status_code=400, detail="source_url is required for URL ingestion")
        scraped = scraper(source_url)
        item = ItemCreate(
            title=title or scraped['title'],
            content=scraped['content'],
            source_type='url',
            source_url=source_url,
            tags=tags,
        )

    elif source_type.lower() == 'pdf':
        if not file:
            raise HTTPException(status_code=400, detail="File is required for PDF ingestion")
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        file_data = await file.read()
        extracted = extract_pdf(file_data)
        item = ItemCreate(
            title=title or file.filename,
            content=extracted['content'],
            source_type='pdf',
            tags=tags,
        )

    elif source_type.lower() in ['voice', 'mp3', 'audio']:
        if not file:
            raise HTTPException(status_code=400, detail="File is required for audio ingestion")
        file_data = await file.read()
        extracted = extract_voice(file_data)
        item = ItemCreate(
            title=title or file.filename,
            content=extracted['content'],
            source_type='audio',
            tags=tags,
        )

    elif source_type.lower() == 'telegram_message':
        if not content:
            raise HTTPException(status_code=400, detail="No content in telegram message")
        item = ItemCreate(
            title=title or f"Telegram — {content[:40]}",
            content=content,
            source_type='telegram',
            tags=tags,
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source_type: {source_type}")

    db_item = await save_db(item, db)

    # ── Critical Fix: Don't pass db to background task ───────
    # The request's db session closes after this route returns.
    # embed_and_store now creates its own session internally.
    background_tasks.add_task(embed_and_store, db_item.id, db_item.content)

    return db_item