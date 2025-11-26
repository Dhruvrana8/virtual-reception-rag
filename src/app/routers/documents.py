from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, dependencies
from ..services import s3

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Upload to S3
    s3_url = s3.upload_file_to_s3(file, file.filename)
    if not s3_url:
        raise HTTPException(status_code=500, detail="Failed to upload to S3")
    
    # Save to DB
    db_document = models.Document(filename=file.filename, s3_key=file.filename)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Trigger RAG ingestion (Placeholder for now, or call actual pipeline)
    # TODO: Add ingestion logic here
    
    return db_document

@router.get("/", response_model=List[schemas.Document])
def read_documents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return documents
