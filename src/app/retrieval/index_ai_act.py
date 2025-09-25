"""AI Act corpus indexer for EU AI Act compliance RAG system."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from src.core.config import settings


class AIActIndexer:
    """Indexer for EU AI Act corpus with compliance-focused chunking."""
    
    def __init__(self) -> None:
        """Initialize AI Act indexer."""
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_ai_act_corpus(self, corpus_dir: str = "data/knowledge/ai_act") -> List[Document]:
        """Load EU AI Act documents from corpus directory."""
        corpus_path = Path(corpus_dir)
        if not corpus_path.exists():
            raise FileNotFoundError(f"AI Act corpus directory not found: {corpus_dir}")
            
        documents = []
        for file_path in corpus_path.glob("*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Create document with enhanced metadata for compliance
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "filename": file_path.name,
                        "document_type": "ai_act",
                        "compliance_focus": True,
                        "risk_category": self._extract_risk_category(content),
                        "article_references": self._extract_article_references(content)
                    }
                )
                documents.append(doc)
                self.logger.info(f"Loaded AI Act document: {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                continue
                
        if not documents:
            raise ValueError(f"No AI Act documents found in {corpus_dir}")
            
        self.logger.info(f"Loaded {len(documents)} AI Act documents")
        return documents
    
    def _extract_risk_category(self, content: str) -> str:
        """Extract risk category from document content."""
        content_lower = content.lower()
        
        if "prohibited" in content_lower:
            return "prohibited"
        elif "high-risk" in content_lower:
            return "high-risk"
        elif "limited risk" in content_lower:
            return "limited-risk"
        elif "minimal risk" in content_lower:
            return "minimal-risk"
        else:
            return "general"
    
    def _extract_article_references(self, content: str) -> List[str]:
        """Extract article references from document content."""
        import re
        
        # Look for article references like "Article 5", "Art. 10", etc.
        article_patterns = [
            r"Article\s+(\d+)",
            r"Art\.\s*(\d+)",
            r"article\s+(\d+)",
            r"art\.\s*(\d+)"
        ]
        
        references = []
        for pattern in article_patterns:
            matches = re.findall(pattern, content)
            references.extend([f"Article {match}" for match in matches])
            
        return list(set(references))  # Remove duplicates
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk documents with compliance-focused splitting."""
        chunks = []
        
        for doc in documents:
            # Split document into chunks
            doc_chunks = self.text_splitter.split_documents([doc])
            
            # Enhance each chunk with compliance metadata
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_id": f"{doc.metadata['filename']}_chunk_{i}",
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks),
                    "compliance_keywords": self._extract_compliance_keywords(chunk.page_content)
                })
                chunks.append(chunk)
                
        self.logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def _extract_compliance_keywords(self, content: str) -> List[str]:
        """Extract compliance-related keywords from content."""
        compliance_keywords = [
            "risk", "safety", "security", "privacy", "transparency",
            "accountability", "fairness", "non-discrimination", "human oversight",
            "data governance", "algorithmic transparency", "explainability",
            "audit", "compliance", "conformity", "assessment", "monitoring"
        ]
        
        content_lower = content.lower()
        found_keywords = [kw for kw in compliance_keywords if kw in content_lower]
        return found_keywords
    
    def create_vectorstore(self, chunks: List[Document], output_path: str | None = None) -> FAISS:
        """Create FAISS vectorstore from document chunks."""
        if output_path is None:
            output_path = settings.vectorstore_path
            
        self.logger.info(f"Creating FAISS vectorstore with {len(chunks)} chunks")
        
        # Create FAISS vectorstore
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        
        # Save vectorstore
        os.makedirs(output_path, exist_ok=True)
        vectorstore.save_local(output_path)
        
        self.logger.info(f"Vectorstore saved to {output_path}")
        return vectorstore
    
    def index_ai_act_corpus(self, corpus_dir: str = "data/knowledge/ai_act", output_path: str | None = None) -> FAISS:
        """Complete indexing pipeline for AI Act corpus."""
        self.logger.info("Starting AI Act corpus indexing")
        
        # Load documents
        documents = self.load_ai_act_corpus(corpus_dir)
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Create vectorstore
        vectorstore = self.create_vectorstore(chunks, output_path)
        
        self.logger.info("AI Act corpus indexing completed successfully")
        return vectorstore


def main():
    """Main function for AI Act indexing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index EU AI Act corpus")
    parser.add_argument(
        "--corpus-dir",
        default="data/knowledge/ai_act",
        help="Path to AI Act corpus directory"
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Path to save vectorstore"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        # Create indexer
        indexer = AIActIndexer()
        
        # Index corpus
        vectorstore = indexer.index_ai_act_corpus(
            corpus_dir=args.corpus_dir,
            output_path=args.output_path
        )
        
        print("✅ AI Act corpus indexing completed successfully")
        print(f"📁 Vectorstore saved to: {args.output_path or settings.vectorstore_path}")
        
    except Exception as e:
        print(f"❌ Error indexing AI Act corpus: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
