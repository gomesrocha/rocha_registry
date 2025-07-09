from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Manifest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    reference: str
    digest: str = Field(index=True)
    content_type: str
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    
    class Config:
        indexes = ["name", "reference"]