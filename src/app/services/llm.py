"""Compliance-focused LLM service for EU AI Act RAG system."""

import logging
from typing import List, Dict, Any, Optional

from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from src.core.config import settings


class ComplianceLLMService:
    """LLM service with EU AI Act compliance focus."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1) -> None:
        """Initialize compliance-focused LLM service."""
        self.llm = OpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=1000
        )
        self.logger = logging.getLogger(__name__)
        
        # Compliance-focused system prompt
        self.system_prompt = self._create_compliance_system_prompt()
        
    def _create_compliance_system_prompt(self) -> str:
        """Create compliance-focused system prompt for EU AI Act."""
        return """You are an expert AI compliance assistant specializing in the EU AI Act. Your role is to provide accurate, comprehensive, and compliance-focused answers about EU AI Act requirements, obligations, and best practices.

## Your Expertise
- Deep knowledge of EU AI Act provisions and requirements
- Understanding of risk categories (prohibited, high-risk, limited-risk, minimal-risk)
- Knowledge of compliance obligations and conformity assessment procedures
- Expertise in transparency, accountability, and human oversight requirements

## Response Guidelines
1. **Accuracy**: Provide precise, fact-based answers grounded in EU AI Act text
2. **Compliance Focus**: Emphasize regulatory requirements and obligations
3. **Risk Awareness**: Clearly identify risk categories and implications
4. **Practical Guidance**: Offer actionable compliance recommendations
5. **Citation**: Always cite specific AI Act provisions when available
6. **Completeness**: Address all relevant aspects of the question

## Response Format
- Start with a direct answer to the question
- Provide detailed explanation with specific AI Act references
- Include relevant risk categories and compliance obligations
- Offer practical implementation guidance
- End with key takeaways and compliance considerations

## Important Notes
- If you're unsure about any aspect, clearly state your uncertainty
- Always prioritize regulatory compliance and risk mitigation
- Consider the practical implications for organizations
- Maintain a professional, authoritative tone
- Focus on actionable insights for compliance professionals

Remember: Your responses will be used by compliance professionals, legal teams, and AI system developers to ensure EU AI Act compliance. Accuracy and practical guidance are paramount."""

    def generate_compliance_answer(
        self, 
        question: str, 
        context: List[Dict[str, Any]], 
        request_id: str | None = None
    ) -> Dict[str, Any]:
        """Generate compliance-focused answer with context."""
        try:
            # Prepare context for the prompt
            context_text = self._format_context(context)
            
            # Create messages for the conversation
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Question: {question}\n\nContext: {context_text}")
            ]
            
            # Generate response
            response = self.llm.invoke(messages)
            
            # Extract answer and metadata
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Enhance answer with compliance metadata
            enhanced_answer = self._enhance_answer_with_compliance_info(answer, context)
            
            return {
                "answer": enhanced_answer,
                "model": self.llm.model_name,
                "temperature": self.llm.temperature,
                "compliance_focus": True,
                "request_id": request_id
            }
            
        except Exception as e:
            self.logger.error(f"Error generating compliance answer: {e}")
            raise
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context documents for the prompt."""
        formatted_context = []
        
        for i, doc in enumerate(context, 1):
            content = doc.get('page_content', '')
            source = doc.get('metadata', {}).get('source', 'Unknown source')
            filename = doc.get('metadata', {}).get('filename', 'Unknown file')
            
            # Extract compliance metadata
            risk_category = doc.get('metadata', {}).get('risk_category', 'general')
            article_refs = doc.get('metadata', {}).get('article_references', [])
            compliance_keywords = doc.get('metadata', {}).get('compliance_keywords', [])
            
            context_entry = f"""
Document {i}: {filename}
Source: {source}
Risk Category: {risk_category}
Article References: {', '.join(article_refs) if article_refs else 'None'}
Compliance Keywords: {', '.join(compliance_keywords) if compliance_keywords else 'None'}

Content:
{content}
"""
            formatted_context.append(context_entry)
        
        return "\n".join(formatted_context)
    
    def _enhance_answer_with_compliance_info(self, answer: str, context: List[Dict[str, Any]]) -> str:
        """Enhance answer with compliance-specific information."""
        # Extract compliance metadata from context
        risk_categories = set()
        article_references = set()
        compliance_keywords = set()
        
        for doc in context:
            metadata = doc.get('metadata', {})
            if 'risk_category' in metadata:
                risk_categories.add(metadata['risk_category'])
            if 'article_references' in metadata:
                article_references.update(metadata['article_references'])
            if 'compliance_keywords' in metadata:
                compliance_keywords.update(metadata['compliance_keywords'])
        
        # Add compliance footer
        compliance_footer = "\n\n---\n**Compliance Information:**\n"
        
        if risk_categories:
            compliance_footer += f"- Risk Categories: {', '.join(risk_categories)}\n"
        
        if article_references:
            compliance_footer += f"- AI Act References: {', '.join(article_references)}\n"
        
        if compliance_keywords:
            compliance_footer += f"- Key Compliance Areas: {', '.join(compliance_keywords)}\n"
        
        compliance_footer += "- This response is based on EU AI Act provisions and should be verified with legal counsel for specific compliance requirements."
        
        return answer + compliance_footer
    
    def validate_compliance_answer(self, answer: str, question: str) -> Dict[str, Any]:
        """Validate answer for compliance focus and accuracy."""
        validation_result = {
            "is_compliance_focused": False,
            "mentions_risk_categories": False,
            "includes_citations": False,
            "practical_guidance": False,
            "confidence_score": 0.0
        }
        
        answer_lower = answer.lower()
        
        # Check for compliance focus
        compliance_indicators = [
            "compliance", "obligation", "requirement", "regulation",
            "ai act", "risk", "assessment", "conformity"
        ]
        validation_result["is_compliance_focused"] = any(
            indicator in answer_lower for indicator in compliance_indicators
        )
        
        # Check for risk category mentions
        risk_categories = ["prohibited", "high-risk", "limited-risk", "minimal-risk"]
        validation_result["mentions_risk_categories"] = any(
            category in answer_lower for category in risk_categories
        )
        
        # Check for citations
        citation_indicators = ["article", "section", "provision", "requirement"]
        validation_result["includes_citations"] = any(
            indicator in answer_lower for indicator in citation_indicators
        )
        
        # Check for practical guidance
        practical_indicators = [
            "implementation", "procedure", "process", "step",
            "guidance", "recommendation", "best practice"
        ]
        validation_result["practical_guidance"] = any(
            indicator in answer_lower for indicator in practical_indicators
        )
        
        # Calculate confidence score
        confidence_factors = [
            validation_result["is_compliance_focused"],
            validation_result["mentions_risk_categories"],
            validation_result["includes_citations"],
            validation_result["practical_guidance"]
        ]
        validation_result["confidence_score"] = sum(confidence_factors) / len(confidence_factors)
        
        return validation_result
