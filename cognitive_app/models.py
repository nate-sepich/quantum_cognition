# models.py

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class NodeModel(BaseModel):
    name: str
    label: str
    properties: Dict[str, Any] = {}
    # importance: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    # novelty: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    # confidence: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('name', 'label')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Must not be empty')
        return v.strip()

class RelationshipModel(BaseModel):
    from_node: str
    to_node: str
    type: str
    properties: Dict[str, Any] = {}
