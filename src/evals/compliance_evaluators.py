"""Compliance-focused evaluation service for EU AI Act RAG system."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from langsmith import Client

from src.api.schemas import EvaluationReport, EvaluationResult, Source
from src.app.services.rag_pipeline import ComplianceRAGPipeline


class ComplianceEvaluationService:
    """Compliance-focused evaluation service for EU AI Act RAG pipeline."""
    
    def __init__(self, compliance_pipeline: ComplianceRAGPipeline) -> None:
        """Initialize compliance evaluation service."""
        self.compliance_pipeline = compliance_pipeline
        self.langsmith_client = Client()
        
    def run_evaluation(
        self, 
        dataset_path: str, 
        output_dir: str | None = None
    ) -> EvaluationReport:
        """Run compliance-focused evaluation on a dataset."""
        # Load dataset
        dataset = self._load_dataset(dataset_path)
        
        # Run evaluation
        results = []
        for item in dataset:
            try:
                # Get compliance-focused answer
                result = self.compliance_pipeline.answer_compliance_question(item["q"])
                
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
                
                # Evaluate compliance focus
                compliance_score = self._evaluate_compliance_focus(
                    question=item["q"],
                    answer=result["answer"],
                    sources=result["sources"]
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
                
                # Add compliance metadata
                eval_result.compliance_score = compliance_score
                eval_result.compliance_metadata = result.get("compliance_metadata", {})
                
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
        avg_compliance = sum(getattr(r, 'compliance_score', 0) for r in results) / len(results)
        
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
        
        # Add compliance metadata
        report.compliance_metadata = {
            "avg_compliance_score": avg_compliance,
            "compliance_focus": True,
            "evaluation_type": "compliance_focused"
        }
        
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
    
    def _evaluate_compliance_focus(
        self, 
        question: str, 
        answer: str, 
        sources: List[Source]
    ) -> float:
        """Evaluate compliance focus of the answer."""
        answer_lower = answer.lower()
        
        # Compliance indicators
        compliance_indicators = [
            "compliance", "obligation", "requirement", "regulation",
            "ai act", "risk", "assessment", "conformity", "audit",
            "transparency", "accountability", "human oversight"
        ]
        
        # Count compliance indicators
        compliance_count = sum(1 for indicator in compliance_indicators if indicator in answer_lower)
        
        # Normalize score
        max_indicators = len(compliance_indicators)
        return min(compliance_count / max_indicators, 1.0)
    
    def _save_report(self, report: EvaluationReport, output_dir: str) -> None:
        """Save evaluation report to file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = output_path / f"{timestamp}_compliance_run"
        report_dir.mkdir(exist_ok=True)
        
        # Save report as JSON
        report_file = report_dir / "compliance_evaluation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report.dict(), f, indent=2, ensure_ascii=False)
        
        # Save detailed results
        results_file = report_dir / "detailed_compliance_results.jsonl"
        with open(results_file, "w", encoding="utf-8") as f:
            for result in report.results:
                json.dump(result.dict(), f, ensure_ascii=False)
                f.write("\n")
        
        print(f"Compliance evaluation report saved to {report_dir}")
