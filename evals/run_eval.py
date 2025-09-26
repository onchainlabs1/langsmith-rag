#!/usr/bin/env python3
"""
LangSmith Evaluation Script for EU AI Act RAG System.

This script runs comprehensive evaluations using built-in and custom evaluators
to assess the quality and compliance of the RAG system responses.
"""

import os
import sys
import csv
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from langsmith import Client, evaluate
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langsmith.schemas import Run, Example
from langchain_core.evaluators import load_evaluator

from src.services.groq_langchain_rag import GroqLangChainRAG
from src.services.langchain_rag import langchain_rag
from src.core.observability import get_observability_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationCoverageEvaluator(LangChainStringEvaluator):
    """Custom evaluator for citation coverage in RAG responses."""
    
    def __init__(self):
        super().__init__()
    
    def _evaluate_strings(
        self,
        prediction: str,
        reference: Optional[str] = None,
        input: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Evaluate citation coverage in the prediction."""
        # Extract citations from prediction (looking for patterns like "Article X", "EU AI Act", etc.)
        citation_patterns = [
            r"Article \d+",
            r"EU AI Act",
            r"Annex [IV]+",
            r"Chapter \d+"
        ]
        
        import re
        citations_found = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, prediction, re.IGNORECASE)
            citations_found.extend(matches)
        
        # Expected citations from reference
        expected_citations = []
        if reference:
            for pattern in citation_patterns:
                matches = re.findall(pattern, reference, re.IGNORECASE)
                expected_citations.extend(matches)
        
        # Calculate coverage score
        if expected_citations:
            coverage = len(set(citations_found)) / len(set(expected_citations))
        else:
            coverage = 1.0 if citations_found else 0.0
        
        return {
            "key": "citation_coverage",
            "score": coverage,
            "value": coverage,
            "reasoning": f"Found {len(citations_found)} citations out of {len(expected_citations)} expected"
        }


class RegulatoryScopeEvaluator(LangChainStringEvaluator):
    """Custom evaluator for regulatory scope matching."""
    
    def __init__(self):
        super().__init__()
    
    def _evaluate_strings(
        self,
        prediction: str,
        reference: Optional[str] = None,
        input: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Evaluate if the prediction matches the regulatory scope."""
        # Extract regulatory scope from kwargs
        regulatory_scope = kwargs.get("regulatory_scope", "")
        
        # Check if prediction contains scope-relevant terms
        scope_terms = regulatory_scope.lower().split()
        prediction_lower = prediction.lower()
        
        matches = sum(1 for term in scope_terms if term in prediction_lower)
        scope_score = matches / len(scope_terms) if scope_terms else 1.0
        
        return {
            "key": "regulatory_scope_match",
            "score": scope_score,
            "value": scope_score,
            "reasoning": f"Matched {matches}/{len(scope_terms)} regulatory scope terms"
        }


class RAGEvaluationRunner:
    """Main evaluation runner for the RAG system."""
    
    def __init__(self, project_name: str = "eu-ai-act-rag-evals"):
        """Initialize the evaluation runner."""
        self.client = Client()
        self.project_name = project_name
        self.rag_system = None
        self.observability = get_observability_service()
        
        # Initialize evaluators
        self.evaluators = {
            "faithfulness": load_evaluator("faithfulness"),
            "correctness": load_evaluator("correctness"), 
            "helpfulness": load_evaluator("helpfulness"),
            "citation_coverage": CitationCoverageEvaluator(),
            "regulatory_scope": RegulatoryScopeEvaluator()
        }
    
    def load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load evaluation dataset from CSV."""
        dataset = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset.append(row)
        return dataset
    
    def setup_rag_system(self, provider: str = "groq"):
        """Setup the RAG system for evaluation."""
        try:
            if provider == "groq":
                self.rag_system = GroqLangChainRAG()
                self.rag_system.load_documents()
            else:
                self.rag_system = langchain_rag
            logger.info(f"RAG system initialized with provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def create_dataset(self, dataset: List[Dict[str, Any]]) -> str:
        """Create a LangSmith dataset from the evaluation data."""
        examples = []
        for i, row in enumerate(dataset):
            example = Example(
                inputs={"question": row["question"]},
                outputs={
                    "expected_answer": row["expected_answer"],
                    "context": row["context"],
                    "regulatory_scope": row["regulatory_scope"],
                    "expected_citations": row["expected_citations"]
                }
            )
            examples.append(example)
        
        dataset_name = f"{self.project_name}-dataset"
        dataset = self.client.create_dataset(
            dataset_name=dataset_name,
            description="EU AI Act compliance evaluation dataset"
        )
        
        self.client.create_examples(
            inputs=[ex.inputs for ex in examples],
            outputs=[ex.outputs for ex in examples],
            dataset_id=dataset.id
        )
        
        logger.info(f"Created dataset with {len(examples)} examples")
        return dataset.id
    
    def run_evaluation(self, dataset_id: str, provider: str = "groq") -> str:
        """Run comprehensive evaluation on the dataset."""
        
        def rag_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Wrapper function for RAG system evaluation."""
            question = inputs["question"]
            
            try:
                # Get answer from RAG system
                if hasattr(self.rag_system, 'answer_question'):
                    result = self.rag_system.answer_question(question)
                    answer = result.get("answer", "")
                    sources = result.get("sources", [])
                else:
                    # Fallback for different RAG system interface
                    result = self.rag_system.answer_question(question)
                    answer = result.get("answer", "")
                    sources = result.get("sources", [])
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "provider": provider
                }
            except Exception as e:
                logger.error(f"Error in RAG evaluation: {e}")
                return {
                    "answer": f"Error: {str(e)}",
                    "sources": [],
                    "provider": provider
                }
        
        # Run evaluation
        results = evaluate(
            lambda inputs: rag_function(inputs),
            data=dataset_id,
            evaluators=list(self.evaluators.values()),
            experiment_prefix=f"eu-ai-act-{provider}",
            description=f"EU AI Act RAG evaluation with {provider} provider",
            metadata={
                "provider": provider,
                "evaluation_type": "comprehensive",
                "regulatory_framework": "EU AI Act"
            }
        )
        
        logger.info(f"Evaluation completed. Results: {results}")
        return results["experiment_name"]
    
    def run_quick_eval(self, questions: List[str], provider: str = "groq") -> Dict[str, Any]:
        """Run quick evaluation on a list of questions."""
        if not self.rag_system:
            self.setup_rag_system(provider)
        
        results = []
        for question in questions:
            try:
                result = self.rag_system.answer_question(question)
                results.append({
                    "question": question,
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "provider": provider
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "sources": [],
                    "provider": provider
                })
        
        return {
            "provider": provider,
            "total_questions": len(questions),
            "results": results
        }


def main():
    """Main evaluation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run EU AI Act RAG evaluations")
    parser.add_argument("--provider", choices=["groq", "openai"], default="groq",
                       help="LLM provider to use")
    parser.add_argument("--dataset", default="evals/datasets/ai_act_eval.csv",
                       help="Path to evaluation dataset")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick evaluation instead of full dataset")
    parser.add_argument("--questions", nargs="+",
                       help="Questions for quick evaluation")
    
    args = parser.parse_args()
    
    # Initialize evaluation runner
    runner = RAGEvaluationRunner()
    
    try:
        if args.quick:
            # Quick evaluation
            questions = args.questions or [
                "What are high-risk AI systems under the EU AI Act?",
                "What are the penalties for non-compliance?",
                "When does the EU AI Act come into effect?"
            ]
            
            logger.info("Running quick evaluation...")
            results = runner.run_quick_eval(questions, args.provider)
            
            print("\n" + "="*50)
            print("QUICK EVALUATION RESULTS")
            print("="*50)
            for result in results["results"]:
                print(f"\nQ: {result['question']}")
                print(f"A: {result['answer'][:200]}...")
                print(f"Sources: {len(result['sources'])}")
            
        else:
            # Full dataset evaluation
            logger.info("Loading evaluation dataset...")
            dataset = runner.load_dataset(args.dataset)
            
            logger.info("Setting up RAG system...")
            runner.setup_rag_system(args.provider)
            
            logger.info("Creating LangSmith dataset...")
            dataset_id = runner.create_dataset(dataset)
            
            logger.info("Running evaluation...")
            experiment_name = runner.run_evaluation(dataset_id, args.provider)
            
            print(f"\n✅ Evaluation completed!")
            print(f"📊 Experiment: {experiment_name}")
            print(f"🔗 View results: https://smith.langchain.com/experiments")
            
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
