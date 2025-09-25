"""RAG pipeline service with LangSmith tracing."""

import uuid
from typing import List, Dict, Any

from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langsmith import Client

from src.core.config import settings
from src.services.vectorstore import VectorStoreService


class RAGService:
    """RAG pipeline service with LangSmith tracing."""
    
    def __init__(self, vectorstore_service: VectorStoreService) -> None:
        """Initialize RAG service."""
        self.vectorstore_service = vectorstore_service
        self.llm = OpenAI(temperature=0)
        self.langsmith_client = Client()
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context:
            {context}

            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain
        self.retrieval_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore_service.get_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
    def answer_question(
        self, 
        question: str, 
        request_id: str | None = None
    ) -> Dict[str, Any]:
        """Answer a question using RAG pipeline with LangSmith tracing."""
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        # Create LangSmith run for tracing
        with self.langsmith_client.trace(
            name="rag_pipeline",
            run_type="chain",
            inputs={"question": question},
            project_name=settings.langchain_project,
            tags=["rag", "production"],
            metadata={"request_id": request_id}
        ) as trace:
            try:
                # Run retrieval chain
                result = self.retrieval_chain({"query": question})
                
                # Extract answer and sources
                answer = result["result"]
                source_docs = result["source_documents"]
                
                # Format sources
                sources = []
                for doc in source_docs:
                    sources.append({
                        "content": doc.page_content[:200] + "...",
                        "source": doc.metadata.get("source", "unknown"),
                        "filename": doc.metadata.get("filename", "unknown")
                    })
                
                # Log trace outputs
                trace.outputs = {
                    "answer": answer,
                    "sources": sources,
                    "num_sources": len(sources)
                }
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "trace_url": f"https://smith.langchain.com/trace/{trace.id}",
                    "request_id": request_id
                }
                
            except Exception as e:
                # Log error in trace
                trace.error = str(e)
                raise
