from pydantic import BaseModel
from typing import List

from datetime import datetime


class ItemCreate(BaseModel):
    title: str | None = None
    content: str
    source_type: str
    source_url: str | None = None
    tags : List[str] | None = None

class ItemResponse(BaseModel):
    id: int
    created_at: datetime
    processed: bool 
    title: str | None = None
    content: str
    source_type: str
    source_url: str | None = None
    tags: List[str] | None = None
    model_config = {'from_attributes': True}

class ChunkResult(BaseModel):
    chunk_content: str
    item_title:    str | None = None
    source_type:   str
    item_id:       int