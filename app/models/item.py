from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from app.db import Base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import ARRAY

class Item(Base):
    __tablename__ = 'items'
    id =            Column(Integer, primary_key=True)
    title =         Column(String, nullable=True)
    content =       Column(Text, nullable=False)
    source_type =   Column(String)
    source_url =    Column(String, nullable=True)
    tags =          Column(ARRAY(String), nullable=True)
    created_at =    Column(DateTime(timezone=True), server_default=func.now())
    processed =     Column(Boolean, default=False)
    embedding =     Column(Vector(1024), nullable=True)