# backend/schemas.py
from pydantic import BaseModel

class SummaryRequest(BaseModel):
    category: str
    url: str