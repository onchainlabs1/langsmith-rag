"""Advanced conversation memory management for EU AI Act Compliance RAG."""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from langchain.memory import (
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationEntityMemory,
    ConversationKGMemory
)
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from src.core.config import settings


@dataclass
class ConversationContext:
    """Conversation context data structure."""
    session_id: str
    user_id: Optional[str]
    timestamp: datetime
    topic: str
    compliance_focus: bool
    risk_categories: List[str]
    article_references: List[str]
    conversation_summary: str
    metadata: Dict[str, Any]


class AdvancedConversationMemory:
    """Advanced conversation memory with multiple memory types."""
    
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        """Initialize advanced conversation memory."""
        self.session_id = session_id
        self.user_id = user_id
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM for summarization
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=500
        )
        
        # Initialize different memory types
        self._initialize_memories()
        
        # Conversation context
        self.context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now(),
            topic="EU AI Act Compliance",
            compliance_focus=True,
            risk_categories=[],
            article_references=[],
            conversation_summary="",
            metadata={}
        )
    
    def _initialize_memories(self):
        """Initialize different types of memory."""
        # Buffer window memory (recent conversation)
        self.buffer_memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            memory_key="chat_history",
            return_messages=True
        )
        
        # Summary buffer memory (long-term summarization)
        self.summary_memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Entity memory (for compliance entities)
        self.entity_memory = ConversationEntityMemory(
            llm=self.llm,
            memory_key="compliance_entities",
            return_messages=True
        )
        
        # Knowledge graph memory (for compliance relationships)
        self.kg_memory = ConversationKGMemory(
            llm=self.llm,
            memory_key="compliance_kg",
            return_messages=True
        )
    
    def add_interaction(
        self, 
        question: str, 
        answer: str, 
        sources: List[Dict[str, Any]] = None,
        compliance_metadata: Dict[str, Any] = None
    ):
        """Add interaction to all memory types."""
        try:
            # Add to buffer memory
            self.buffer_memory.save_context(
                {"input": question},
                {"output": answer}
            )
            
            # Add to summary memory
            self.summary_memory.save_context(
                {"input": question},
                {"output": answer}
            )
            
            # Add to entity memory
            self.entity_memory.save_context(
                {"input": question},
                {"output": answer}
            )
            
            # Add to knowledge graph memory
            self.kg_memory.save_context(
                {"input": question},
                {"output": answer}
            )
            
            # Update context
            self._update_context(question, answer, sources, compliance_metadata)
            
            self.logger.info(f"Added interaction to memory for session {self.session_id}")
            
        except Exception as e:
            self.logger.error(f"Error adding interaction to memory: {e}")
            raise
    
    def _update_context(
        self, 
        question: str, 
        answer: str, 
        sources: List[Dict[str, Any]] = None,
        compliance_metadata: Dict[str, Any] = None
    ):
        """Update conversation context with new information."""
        # Update risk categories
        if compliance_metadata and 'risk_categories' in compliance_metadata:
            for category in compliance_metadata['risk_categories']:
                if category not in self.context.risk_categories:
                    self.context.risk_categories.append(category)
        
        # Update article references
        if compliance_metadata and 'article_references' in compliance_metadata:
            for article in compliance_metadata['article_references']:
                if article not in self.context.article_references:
                    self.context.article_references.append(article)
        
        # Update metadata
        if compliance_metadata:
            self.context.metadata.update(compliance_metadata)
        
        # Update timestamp
        self.context.timestamp = datetime.now()
    
    def get_conversation_history(self, memory_type: str = "buffer") -> List[BaseMessage]:
        """Get conversation history from specified memory type."""
        try:
            if memory_type == "buffer":
                return self.buffer_memory.chat_memory.messages
            elif memory_type == "summary":
                return self.summary_memory.chat_memory.messages
            elif memory_type == "entity":
                return self.entity_memory.chat_memory.messages
            elif memory_type == "kg":
                return self.kg_memory.chat_memory.messages
            else:
                raise ValueError(f"Unknown memory type: {memory_type}")
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_conversation_summary(self) -> str:
        """Get conversation summary."""
        try:
            if hasattr(self.summary_memory, 'predict_new_summary'):
                messages = self.summary_memory.chat_memory.messages
                return self.summary_memory.predict_new_summary(messages, "")
            else:
                return "No conversation summary available"
        except Exception as e:
            self.logger.error(f"Error getting conversation summary: {e}")
            return "Error generating summary"
    
    def get_compliance_entities(self) -> Dict[str, Any]:
        """Get compliance entities from entity memory."""
        try:
            return self.entity_memory.entity_store.store
        except Exception as e:
            self.logger.error(f"Error getting compliance entities: {e}")
            return {}
    
    def get_compliance_knowledge_graph(self) -> Dict[str, Any]:
        """Get compliance knowledge graph."""
        try:
            return self.kg_memory.kg.get_triples()
        except Exception as e:
            self.logger.error(f"Error getting knowledge graph: {e}")
            return {}
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive context summary."""
        return {
            "session_id": self.context.session_id,
            "user_id": self.context.user_id,
            "timestamp": self.context.timestamp.isoformat(),
            "topic": self.context.topic,
            "compliance_focus": self.context.compliance_focus,
            "risk_categories": self.context.risk_categories,
            "article_references": self.context.article_references,
            "conversation_summary": self.get_conversation_summary(),
            "compliance_entities": self.get_compliance_entities(),
            "knowledge_graph_size": len(self.get_compliance_knowledge_graph()),
            "metadata": self.context.metadata
        }
    
    def clear_memory(self, memory_type: str = "all"):
        """Clear specified memory type."""
        try:
            if memory_type in ["all", "buffer"]:
                self.buffer_memory.clear()
            if memory_type in ["all", "summary"]:
                self.summary_memory.clear()
            if memory_type in ["all", "entity"]:
                self.entity_memory.clear()
            if memory_type in ["all", "kg"]:
                self.kg_memory.clear()
            
            # Reset context
            if memory_type == "all":
                self.context.risk_categories = []
                self.context.article_references = []
                self.context.metadata = {}
                self.context.timestamp = datetime.now()
            
            self.logger.info(f"Cleared {memory_type} memory for session {self.session_id}")
            
        except Exception as e:
            self.logger.error(f"Error clearing memory: {e}")
            raise
    
    def export_conversation(self) -> Dict[str, Any]:
        """Export conversation data for analysis."""
        return {
            "context": asdict(self.context),
            "conversation_history": [
                {"type": msg.__class__.__name__, "content": msg.content}
                for msg in self.buffer_memory.chat_memory.messages
            ],
            "compliance_entities": self.get_compliance_entities(),
            "knowledge_graph": self.get_compliance_knowledge_graph(),
            "summary": self.get_conversation_summary(),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "buffer_messages": len(self.buffer_memory.chat_memory.messages),
            "summary_tokens": getattr(self.summary_memory, 'summary_token_count', 0),
            "entity_count": len(self.get_compliance_entities()),
            "kg_triples": len(self.get_compliance_knowledge_graph()),
            "session_duration": (datetime.now() - self.context.timestamp).total_seconds(),
            "risk_categories": len(self.context.risk_categories),
            "article_references": len(self.context.article_references)
        }


class ConversationMemoryManager:
    """Manager for multiple conversation memories."""
    
    def __init__(self):
        """Initialize conversation memory manager."""
        self.memories: Dict[str, AdvancedConversationMemory] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_or_create_memory(self, session_id: str, user_id: Optional[str] = None) -> AdvancedConversationMemory:
        """Get existing memory or create new one."""
        if session_id not in self.memories:
            self.memories[session_id] = AdvancedConversationMemory(session_id, user_id)
            self.logger.info(f"Created new memory for session {session_id}")
        
        return self.memories[session_id]
    
    def remove_memory(self, session_id: str):
        """Remove memory for session."""
        if session_id in self.memories:
            del self.memories[session_id]
            self.logger.info(f"Removed memory for session {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs."""
        return list(self.memories.keys())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Cleanup sessions older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, memory in self.memories.items():
            if memory.context.timestamp < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.remove_memory(session_id)
        
        self.logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global memory statistics."""
        total_sessions = len(self.memories)
        total_messages = sum(
            len(memory.buffer_memory.chat_memory.messages) 
            for memory in self.memories.values()
        )
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_sessions": [session_id for session_id in self.memories.keys()],
            "timestamp": datetime.now().isoformat()
        }


# Global memory manager instance
memory_manager = ConversationMemoryManager()
