from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Remove the enum imports and use strings instead
# from .models import InteractionType, Sentiment

# Define enums as strings for validation
InteractionType = str
Sentiment = str

# User schemas
class UserBase(BaseModel):
    username: str
    full_name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# HCP schemas
class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class HCPCreate(HCPBase):
    pass

class HCPOut(HCPBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Material/Sample schemas
class MaterialBase(BaseModel):
    name: str
    quantity: Optional[int] = 1

class SampleBase(BaseModel):
    product_name: str
    quantity: Optional[int] = 1

# FollowUp schemas
class FollowUpBase(BaseModel):
    action: str
    due_date: Optional[datetime] = None

# Interaction schemas
class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: str  # Changed to str
    date: datetime
    time: str
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None  # Changed to str
    outcome: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None

class InteractionCreate(InteractionBase):
    materials: Optional[List[MaterialBase]] = []
    samples: Optional[List[SampleBase]] = []
    followups: Optional[List[FollowUpBase]] = []

class InteractionUpdate(BaseModel):
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None
    materials: Optional[List[MaterialBase]] = None
    samples: Optional[List[SampleBase]] = None
    followups: Optional[List[FollowUpBase]] = None

class InteractionOut(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    hcp: HCPOut
    user: UserOut
    materials: List[MaterialBase]
    samples: List[SampleBase]
    followups: List[FollowUpBase]

    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    message: str
    interaction_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    extracted_data: Optional[dict] = None
    suggested_followups: Optional[List[str]] = None
    interaction_id: Optional[int] = None