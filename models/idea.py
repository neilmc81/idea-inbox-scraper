
from pydantic import BaseModel
from datetime import datetime

class Idea(BaseModel):
    id: str
    title: str
    description: str
    source: str
    url: str
    created_at: datetime
    score: float = 0.0
