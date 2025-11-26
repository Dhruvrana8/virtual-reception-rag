# Virtual Reception RAG Backend

This is the FastAPI backend for the Virtual Reception RAG application.

## Setup

1.  **Install Dependencies**:

    ```bash
    uv pip install fastapi uvicorn "python-jose[cryptography]" "passlib[bcrypt]" python-multipart sqlalchemy boto3
    ```

2.  **Environment Variables**:
    Ensure your `.env` file has the following variables:

    ```env
    DATABASE_URL=sqlite:///./sql_app.db
    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    AWS_ACCESS_KEY_ID=your-aws-key
    AWS_SECRET_ACCESS_KEY=your-aws-secret
    AWS_REGION=us-east-1
    S3_BUCKET_NAME=your-bucket-name
    ```

3.  **Run the Server**:
    ```bash
    uvicorn src.app.main:app --reload
    ```

## API Endpoints

- **Auth**:
  - `POST /auth/signup`: Register a new user.
  - `POST /auth/token`: Login to get an access token.
- **Documents**:
  - `POST /documents/`: Upload a document to S3 (requires auth).
  - `GET /documents/`: List uploaded documents.
- **Chats**:
  - `POST /chats/`: Create a new chat.
  - `GET /chats/`: List your chats.
  - `POST /chats/{chat_id}/messages`: Send a message and get a RAG response.
  - `GET /chats/{chat_id}`: Get chat history.

## Notes

- The backend uses SQLite by default (`sql_app.db`).
- The RAG pipeline expects the vectorstore to be in `vectorstore/faiss_index`.
