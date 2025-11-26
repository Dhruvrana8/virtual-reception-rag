from pathlib import Path
from typing import Union
import torch

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, Runnable

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline


DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_GEN_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"


class RAGPipeline:
    """
    This version assumes embeddings are ALREADY created & stored in FAISS.
    """

    def __init__(
        self,
        vectorstore_path: Union[str, Path],
        embed_model_name: str = DEFAULT_EMBED_MODEL,
        gen_model_name: str = DEFAULT_GEN_MODEL,
        k_retriever: int = 6,
    ):
        self.vectorstore_path = Path(vectorstore_path)
        self.embed_model_name = embed_model_name
        self.gen_model_name = gen_model_name
        self.k_retriever = k_retriever

        self.retriever = None
        self.rag_chain: Runnable = None

        self._load_vectorstore()
        self._setup_llm_and_chain()

    def _load_vectorstore(self):
        """Loads the FAISS vectorstore built earlier."""

        print(
            f"--- Loading FAISS Vectorstore from {self.vectorstore_path} ---")

        embeddings = HuggingFaceEmbeddings(model_name=self.embed_model_name)

        vectorstore = FAISS.load_local(
            folder_path=self.vectorstore_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": self.k_retriever}
        )

        print("Vectorstore loaded successfully.")

    def _setup_llm_and_chain(self):
        """Initializes the LLM and builds the RAG chain."""

        print(f"--- Loading LLM model: {self.gen_model_name} ---")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.gen_model_name, trust_remote_code=True
        )

        # Load model on CPU first (required for disk offload)
        model = AutoModelForCausalLM.from_pretrained(
            self.gen_model_name,
            dtype="auto",
            trust_remote_code=True,
            device_map="auto",
        )

        # Create generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=300,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
        )

        llm = HuggingFacePipeline(pipeline=pipe)

        # RAG prompt
        template = """You are a helpful assistant. Answer the question using ONLY the provided context.
If the context does not contain the answer, say "I don't know".

Context:
{context}

Question: {question}
Answer:"""

        prompt = PromptTemplate.from_template(template)

        def format_context(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.rag_chain = (
            {
                "context": self.retriever | format_context,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        print("RAG chain is ready.")

    def query(self, question: str) -> str:
        if not self.rag_chain:
            raise RuntimeError("RAG chain not initialized.")
        return self.rag_chain.invoke(question)
