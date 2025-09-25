"""Evaluation services and metrics."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Run, Example

from src.api.schemas import EvaluationReport, EvaluationResult, Source
from src.services.rag import RAGService


class EvaluationService:
    """Evaluation service for RAG pipeline."""
    
    def __init__(self, rag_service: RAGService) -> None:
        """Initialize evaluation service."""
        self.rag_service = rag_service
        self.langsmith_client = Client()
        
    def run_evaluation(
        self, 
        dataset_path: str, 
        output_dir: str | None = None
    ) -> EvaluationReport:
        """Run offline evaluation on a dataset."""
        # Load dataset
        dataset = self._load_dataset(dataset_path)
        
        # Run evaluation
        results = []
        for item in dataset:
            try:
                # Get answer from RAG service
                result = self.rag_service.answer_question(item["q"])
                
                # Evaluate groundedness and correctness
                groundedness_score = self._evaluate_groundedness(
                    question=item["q"],
                    answer=result["answer"],
                    sources=result["sources"]
                )
                
                correctness_score = self._evaluate_correctness(
                    question=item["q"],
                    answer=result["answer"],
                    reference=item["reference"]
                )
                
                # Create evaluation result
                eval_result = EvaluationResult(
                    question=item["q"],
                    reference=item["reference"],
                    answer=result["answer"],
                    sources=result["sources"],
                    groundedness_score=groundedness_score,
                    correctness_score=correctness_score,
                    trace_url=result["trace_url"],
                    request_id=result["request_id"]
                )
                
                results.append(eval_result)
                
            except Exception as e:
                # Log error and continue
                print(f"Error evaluating question '{item['q']}': {e}")
                continue
        
        # Calculate aggregate metrics
        if not results:
            raise ValueError("No successful evaluations")
            
        avg_groundedness = sum(r.groundedness_score for r in results) / len(results)
        avg_correctness = sum(r.correctness_score for r in results) / len(results)
        
        # Check if thresholds are met
        passed_threshold = avg_groundedness >= 0.75 and avg_correctness >= 0.70
        
        # Create report
        report = EvaluationReport(
            total_questions=len(dataset),
            avg_groundedness=avg_groundedness,
            avg_correctness=avg_correctness,
            passed_threshold=passed_threshold,
            results=results
        )
        
        # Save report if output directory specified
        if output_dir:
            self._save_report(report, output_dir)
            
        return report
    
    def _load_dataset(self, dataset_path: str) -> List[Dict[str, str]]:
        """Load evaluation dataset from JSONL file."""
        dataset = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    dataset.append(json.loads(line))
        return dataset
    
    def _evaluate_groundedness(
        self, 
        question: str, 
        answer: str, 
        sources: List[Source]
    ) -> float:
        """Evaluate how well the answer is grounded in the sources."""
        # Simple groundedness evaluation
        # In production, use a more sophisticated LLM-based evaluator
        
        if not sources:
            return 0.0
            
        # Check if answer contains information from sources
        source_text = " ".join([s.content for s in sources])
        answer_lower = answer.lower()
        source_lower = source_text.lower()
        
        # Simple keyword overlap scoring
        answer_words = set(answer_lower.split())
        source_words = set(source_lower.split())
        
        if not answer_words:
            return 0.0
            
        overlap = len(answer_words.intersection(source_words))
        total_words = len(answer_words)
        
        return min(overlap / total_words, 1.0)
    
    def _evaluate_correctness(
        self, 
        question: str, 
        answer: str, 
        reference: str
    ) -> float:
        """Evaluate correctness against reference answer."""
        # Simple correctness evaluation
        # In production, use a more sophisticated LLM-based evaluator
        
        answer_lower = answer.lower()
        reference_lower = reference.lower()
        
        # Simple keyword overlap scoring
        answer_words = set(answer_lower.split())
        reference_words = set(reference_lower.split())
        
        if not answer_words or not reference_words:
            return 0.0
            
        overlap = len(answer_words.intersection(reference_words))
        total_reference_words = len(reference_words)
        
        return min(overlap / total_reference_words, 1.0)
    
    def _save_report(self, report: EvaluationReport, output_dir: str) -> None:
        """Save evaluation report to file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = output_path / f"{timestamp}_run"
        report_dir.mkdir(exist_ok=True)
        
        # Save report as JSON
        report_file = report_dir / "evaluation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report.dict(), f, indent=2, ensure_ascii=False)
        
        # Save detailed results
        results_file = report_dir / "detailed_results.jsonl"
        with open(results_file, "w", encoding="utf-8") as f:
            for result in report.results:
                json.dump(result.dict(), f, ensure_ascii=False)
                f.write("\n")
        
        print(f"Evaluation report saved to {report_dir}")
