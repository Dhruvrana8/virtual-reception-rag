import os
from ...rag_pipeline import RAGPipeline
from pathlib import Path

# Assuming the vectorstore is at the project root's vectorstore directory
# We might need to adjust the path relative to where the app is run
VECTORSTORE_PATH = Path("../../vectorstore").resolve()

_rag_pipeline = None

def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        if os.path.exists(VECTORSTORE_PATH):
            try:
                # We might need to check if it's a valid FAISS index
                _rag_pipeline = RAGPipeline(vectorstore_path=VECTORSTORE_PATH)
            except Exception as e:
                print(f"Failed to load RAG pipeline: {e}")
                return None
        else:
            print(f"Vectorstore not found at {VECTORSTORE_PATH}")
            return None
    return _rag_pipeline

def generate_response(question: str):
    pipeline = get_rag_pipeline()
    if pipeline:
        return pipeline.query(question)
    return "I'm sorry, but the knowledge base is currently unavailable."
