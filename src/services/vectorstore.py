"""FAISS vectorstore service for document retrieval."""

import os
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.schema import Document

from src.core.config import settings


class VectorStoreService:
    """FAISS vectorstore service."""
    
    def __init__(self) -> None:
        """Initialize vectorstore service."""
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore: FAISS | None = None
        
    def load_knowledge_base(self, knowledge_dir: str = "data/knowledge") -> None:
        """Load documents from knowledge directory into vectorstore."""
        knowledge_path = Path(knowledge_dir)
        if not knowledge_path.exists():
            raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")
            
        documents = []
        for file_path in knowledge_path.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                doc = Document(
                    page_content=content,
                    metadata={"source": str(file_path), "filename": file_path.name}
                )
                documents.append(doc)
        
        if not documents:
            raise ValueError(f"No markdown files found in {knowledge_dir}")
            
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create FAISS vectorstore
        self.vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        # Save vectorstore
        self.save_vectorstore()
    
    def load_ai_act_corpus(self, corpus_dir: str = "data/knowledge/ai_act") -> None:
        """Load EU AI Act corpus with compliance-focused processing."""
        from src.app.retrieval.index_ai_act import AIActIndexer
        
        # Use AI Act indexer for specialized processing
        indexer = AIActIndexer()
        self.vectorstore = indexer.index_ai_act_corpus(corpus_dir, settings.vectorstore_path)
        
    def save_vectorstore(self) -> None:
        """Save vectorstore to disk."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized")
            
        os.makedirs(settings.vectorstore_path, exist_ok=True)
        self.vectorstore.save_local(settings.vectorstore_path)
        
    def load_vectorstore(self) -> None:
        """Load vectorstore from disk."""
        if not os.path.exists(settings.vectorstore_path):
            raise FileNotFoundError(f"Vectorstore not found at {settings.vectorstore_path}")
            
        self.vectorstore = FAISS.load_local(
            settings.vectorstore_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
    def similarity_search(
        self, 
        query: str, 
        k: int = 4
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized")
            
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        return docs_with_scores
        
    def get_retriever(self, k: int = 4):
        """Get retriever for RAG pipeline."""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized")
            
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
