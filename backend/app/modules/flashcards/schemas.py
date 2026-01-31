from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.modules.conversations.models import ConversationStatus

class Pagination(BaseModel):
    page: int 
    limit: int 
    total_items: int 
    total_pages: int 
    has_next: bool
    has_previous: bool 

class ConversationCreate(BaseModel):
    title: str | None = Field(default=None , max_length=255)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, v: str | None ) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None 

    model_config = ConfigDict(extra="ignore")

class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None , max_length=255)
    status: ConversationStatus | None = None 
    metdata: dict | None = None 

    @field_validator("title")
    @classmethod
    def normalize_title(cls, v: str | None ) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None 

    model_config = ConfigDict(extra="ignore")

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str 
    owner_id: str 
    title: str | None 
    status: ConversationStatus 
    # --- Let's get some metadata --- 
    metadata: dict | None = Field(
        default=None,
        validation_alias="metdata_",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime 
    archived_at: datetime | None 
    deleted_at: datetime | None 

class ConversationListResponse(BaseModel):
    data: list[ConversationOut]
    pagination: Pagination