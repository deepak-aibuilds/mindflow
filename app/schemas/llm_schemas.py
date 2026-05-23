from pydantic import BaseModel


class DigestOutput(BaseModel):
    subject: str
    body: str


class ActionItems(BaseModel):
    high_priority: list[str]
    important: list[str]
    quick_wins: list[str]
