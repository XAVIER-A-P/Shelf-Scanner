from typing import Optional, List
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime
from uuid import UUID, uuid4

class Session(SQLModel, table=True):
    session_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScanHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: UUID = Field(foreign_key="session.session_id")
    image_url: str
    detected_book: List[dict] = Field(default=[], sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Preferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: UUID = Field(foreign_key="session.session_id")
    liked_genres: List[str] = Field(default=[], sa_type=JSON)
    favorite_book: List[str] = Field(default=[], sa_type=JSON)