"""Advanced LangChain implementation for EU AI Act Compliance RAG System."""

import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.schema import Document, BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langsmith import Client

from src.core.config import settings
from src.services.vectorstore import VectorStoreService
from src.core.observability import get_observability_service


class AdvancedLangChainService:
    """Advanced LangChain service with enhanced features."""
    
    def __init__(self, vectorstore_service: VectorStoreService) -> None:
        """Initialize advanced LangChain service."""
        self.vectorstore_service = vectorstore_service
        self.langsmith_client = Client()
        self.observability = get_observability_service()
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM with streaming support
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=2000,
            streaming=True
        )
        
        # Initialize memory systems
        self.conversation_memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 exchanges
            memory_key="chat_history",
            return_messages=True
        )
        
        self.summary_memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=1000,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create advanced prompt templates
        self._create_prompt_templates()
        
        # Initialize chains
        self._initialize_chains()
        
    def _create_prompt_templates(self):
        """Create advanced prompt templates."""
        
        # System prompt for compliance focus
        self.system_prompt = """You are an expert EU AI Act compliance assistant with deep knowledge of regulatory requirements, risk assessments, and compliance procedures.

## Your Expertise:
- EU AI Act provisions and requirements
- Risk categorization (prohibited, high-risk, limited-risk, minimal-risk)
- Conformity assessment procedures
- Transparency and accountability obligations
- Human oversight requirements
- Data governance and privacy compliance

## Response Guidelines:
1. **Accuracy**: Provide precise, fact-based answers grounded in EU AI Act text
2. **Compliance Focus**: Always emphasize regulatory requirements and obligations
3. **Risk Awareness**: Clearly identify risk categories and implications
4. **Practical Guidance**: Offer actionable compliance recommendations
5. **Citations**: Always cite specific AI Act provisions when available
6. **Completeness**: Address all relevant aspects comprehensively

## Context Format:
Use the provided context documents to answer questions. If the context doesn't contain sufficient information, clearly state what additional information would be needed.

## Response Structure:
1. Direct answer to the question
2. Detailed explanation with AI Act references
3. Risk categories and compliance obligations
4. Practical implementation guidance
5. Key takeaways and compliance considerations

Remember: Your responses will be used by compliance professionals, legal teams, and AI system developers. Accuracy and practical guidance are paramount."""

        # Main conversation prompt
        self.conversation_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="context")
        ])
        
        # Retrieval prompt for document processing
        self.retrieval_prompt = PromptTemplate(
            template="""Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that incorporates all necessary context.

Chat History:
{chat_history}

Follow-up Question: {input}

Standalone Question:""",
            input_variables=["chat_history", "input"]
        )
        
        # Document processing prompt
        self.document_prompt = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context:
            {context}

            Question: {question}
            
            Answer:""",
            input_variables=["context", "question"]
        )
        
    def _initialize_chains(self):
        """Initialize LangChain chains."""
        try:
            # Create retriever
            self.retriever = self.vectorstore_service.get_retriever()
            
            # Create history-aware retriever
            self.history_aware_retriever = create_history_aware_retriever(
                llm=self.llm,
                retriever=self.retriever,
                prompt=self.retrieval_prompt
            )
            
            # Create document chain
            self.document_chain = create_stuff_documents_chain(
                llm=self.llm,
                prompt=self.document_prompt
            )
            
            # Create main retrieval chain
            self.retrieval_chain = create_retrieval_chain(
                retriever=self.history_aware_retriever,
                combine_docs_chain=self.document_chain
            )
            
            # Create conversational retrieval chain
            self.conversational_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.conversation_memory,
                return_source_documents=True,
                verbose=True
            )
            
            self.logger.info("Successfully initialized LangChain chains")
            
        except Exception as e:
            self.logger.error(f"Error initializing LangChain chains: {e}")
            raise
    
    async def answer_question_streaming(
        self, 
        question: str, 
        request_id: str | None = None,
        use_conversation: bool = True,
        max_sources: int = 5
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Answer question with streaming response."""
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        # Start observability tracing
        with self.observability.trace_rag_pipeline(request_id, question) as span:
            try:
                # Get chat history
                chat_history = self.conversation_memory.chat_memory.messages if use_conversation else []
                
                # Yield initial metadata
                yield {
                    "type": "metadata",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "has_history": len(chat_history) > 0
                }
                
                # Retrieve documents
                with self.observability.trace_retrieval(question, max_sources):
                    retrieved_docs = await self._retrieve_documents_async(question, max_sources)
                    
                    # Yield retrieved documents
                    yield {
                        "type": "sources",
                        "sources": self._format_sources(retrieved_docs),
                        "num_sources": len(retrieved_docs)
                    }
                
                # Generate streaming response
                full_response = ""
                sources = []
                
                async for chunk in self._generate_streaming_response(
                    question, retrieved_docs, chat_history
                ):
                    if chunk.get("type") == "content":
                        full_response += chunk["content"]
                        yield chunk
                    elif chunk.get("type") == "sources":
                        sources = chunk["sources"]
                        yield chunk
                
                # Store in conversation memory
                if use_conversation:
                    self.conversation_memory.save_context(
                        {"input": question},
                        {"output": full_response}
                    )
                
                # Yield final result
                yield {
                    "type": "final",
                    "answer": full_response,
                    "sources": sources,
                    "trace_url": f"https://smith.langchain.com/trace/{span.span_id}",
                    "request_id": request_id,
                    "compliance_metadata": self._generate_compliance_metadata(full_response, retrieved_docs)
                }
                
            except Exception as e:
                self.logger.error(f"Error in streaming response: {e}")
                span.set_status("error", str(e))
                yield {
                    "type": "error",
                    "error": str(e),
                    "request_id": request_id
                }
    
    async def _retrieve_documents_async(self, question: str, max_sources: int) -> List[Document]:
        """Asynchronously retrieve documents."""
        # Run retrieval in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.vectorstore_service.similarity_search(question, k=max_sources)
        )
    
    async def _generate_streaming_response(
        self, 
        question: str, 
        docs: List[Document], 
        chat_history: List[BaseMessage]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming response using LangChain."""
        try:
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create messages
            messages = [
                SystemMessagePromptTemplate.from_template(self.system_prompt),
                *chat_history,
                HumanMessagePromptTemplate.from_template("{input}"),
                HumanMessagePromptTemplate.from_template("Context: {context}")
            ]
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages(messages)
            
            # Create chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Stream response
            async for chunk in chain.astream({
                "input": question,
                "context": context
            }):
                yield {
                    "type": "content",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Yield sources
            yield {
                "type": "sources",
                "sources": self._format_sources(docs)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating streaming response: {e}")
            raise
    
    def _format_sources(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """Format retrieved documents as sources."""
        sources = []
        
        for i, doc in enumerate(docs):
            metadata = doc.metadata or {}
            
            source = {
                "id": i + 1,
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "source": metadata.get("source", "Unknown source"),
                "filename": metadata.get("filename", "Unknown file"),
                "similarity_score": metadata.get("similarity_score", 0.0),
                "compliance_relevance": metadata.get("compliance_relevance", "medium"),
                "risk_implications": metadata.get("risk_implications", []),
                "article_references": metadata.get("article_references", [])
            }
            sources.append(source)
            
        return sources
    
    def _generate_compliance_metadata(self, answer: str, docs: List[Document]) -> Dict[str, Any]:
        """Generate compliance metadata for the response."""
        # Extract risk categories from documents
        risk_categories = set()
        article_references = set()
        
        for doc in docs:
            metadata = doc.metadata or {}
            if 'risk_category' in metadata:
                risk_categories.add(metadata['risk_category'])
            if 'article_references' in metadata:
                article_references.update(metadata['article_references'])
        
        # Analyze answer for compliance indicators
        compliance_score = self._calculate_compliance_score(answer)
        
        return {
            "risk_categories": list(risk_categories),
            "article_references": list(article_references),
            "compliance_score": compliance_score,
            "model": self.llm.model_name,
            "temperature": self.llm.temperature,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_compliance_score(self, answer: str) -> float:
        """Calculate compliance focus score for the answer."""
        compliance_keywords = [
            "compliance", "obligation", "requirement", "regulation",
            "ai act", "risk", "assessment", "conformity", "prohibited",
            "high-risk", "limited-risk", "minimal-risk", "transparency",
            "accountability", "human oversight", "data governance"
        ]
        
        answer_lower = answer.lower()
        matches = sum(1 for keyword in compliance_keywords if keyword in answer_lower)
        
        return min(matches / len(compliance_keywords), 1.0)
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_memory.clear()
        self.summary_memory.clear()
        self.logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation."""
        if hasattr(self.summary_memory, 'predict_new_summary'):
            return self.summary_memory.predict_new_summary(
                self.conversation_memory.chat_memory.messages,
                ""
            )
        return "No conversation summary available"
    
    def get_compliance_insights(self, question: str) -> Dict[str, Any]:
        """Get compliance insights for a question."""
        # Retrieve documents
        docs = self.vectorstore_service.similarity_search(question, k=10)
        
        # Analyze compliance aspects
        risk_categories = set()
        article_references = set()
        compliance_keywords = set()
        
        for doc in docs:
            metadata = doc.metadata or {}
            if 'risk_category' in metadata:
                risk_categories.add(metadata['risk_category'])
            if 'article_references' in metadata:
                article_references.update(metadata['article_references'])
            if 'compliance_keywords' in metadata:
                compliance_keywords.update(metadata['compliance_keywords'])
        
        return {
            "risk_categories": list(risk_categories),
            "article_references": list(article_references),
            "compliance_keywords": list(compliance_keywords),
            "total_documents": len(docs),
            "compliance_focus": True,
            "timestamp": datetime.now().isoformat()
        }
