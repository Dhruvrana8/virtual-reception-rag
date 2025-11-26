from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    chats = relationship("Chat", back_populates="owner")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    owner = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    content = Column(Text)
    role = Column(String) # "user" or "assistant"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))

    chat = relationship("Chat", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    filename = Column(String)
    s3_key = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
