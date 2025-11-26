from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, dependencies
from ..services import rag
import uuid

router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)

@router.post("/", response_model=schemas.Chat)
def create_chat(
    chat: schemas.ChatCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_chat = models.Chat(title=chat.title, user_id=current_user.id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/", response_model=List[schemas.Chat])
def read_chats(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    chats = db.query(models.Chat).filter(models.Chat.user_id == current_user.id).offset(skip).limit(limit).all()
    return chats

@router.get("/{chat_id}", response_model=schemas.Chat)
def read_chat(
    chat_id: uuid.UUID, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == current_user.id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/{chat_id}/messages", response_model=schemas.Message)
def send_message(
    chat_id: uuid.UUID, 
    message: schemas.MessageCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == current_user.id).first()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save user message
    user_msg = models.Message(content=message.content, role="user", chat_id=chat_id)
    db.add(user_msg)
    db.commit()
    
    # Generate response
    response_content = rag.generate_response(message.content)
    
    # Save assistant message
    assistant_msg = models.Message(content=response_content, role="assistant", chat_id=chat_id)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    
    return assistant_msg
