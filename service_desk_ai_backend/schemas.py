from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    role: str = Field(..., regex='^(admin|manager|employee|service_agent)$')
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserRead(UserBase):
    user_id: UUID
    is_active: bool
    failed_attempts: int
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: UUID
    role: str
    exp: int

class TicketBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    attachment_url: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class TicketRead(TicketBase):
    ticket_id: str
    created_by: Optional[UUID]
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    user_id: UUID
    session_id: UUID
    user_message: str
    ai_response: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class KnowledgeBaseBase(BaseModel):
    title: str
    category: Optional[str] = None
    content: str
    keywords: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseRead(KnowledgeBaseBase):
    article_id: UUID
    created_by: Optional[UUID]
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    message: str
    notification_type: Optional[str] = None
    is_read: bool = False

class NotificationRead(NotificationBase):
    notification_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6)
