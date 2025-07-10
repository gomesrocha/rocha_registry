from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

class Blob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    digest: str = Field(index=True, unique=True)
    size: int
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    media_type: str = Field(default="application/octet-stream")

