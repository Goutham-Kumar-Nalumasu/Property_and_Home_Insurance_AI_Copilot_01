from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(default="default-session")
    message: str


class Source(BaseModel):
    document: str
    chunk_id: int
    score: float
    text_preview: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    intent: str
    memory: Dict[str, Any]
    sources: List[Source] = []


class DamageEstimateRequest(BaseModel):
    damage_type: str
    property_size_category: Optional[str] = None
    peril_category: Optional[str] = None
    affected_component: Optional[str] = None


class DamageEstimateResponse(BaseModel):
    found: bool
    message: str
    matches: List[Dict[str, Any]] = []


class ClaimStatusResponse(BaseModel):
    claim_id: str
    status: str
    next_step: str