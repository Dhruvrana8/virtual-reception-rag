from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: UUID
    created_at: datetime
    chat_id: UUID

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: str = "New Chat"

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: UUID
    created_at: datetime
    user_id: UUID
    messages: List[Message] = []

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str

class Document(DocumentBase):
    id: UUID
    s3_key: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
