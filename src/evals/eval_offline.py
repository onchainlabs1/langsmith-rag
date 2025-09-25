"""Offline evaluation script."""

import argparse
import sys
from pathlib import Path

from src.services.vectorstore import VectorStoreService
from src.services.rag import RAGService
from src.evals.evaluators import EvaluationService


def main():
    """Run offline evaluation."""
    parser = argparse.ArgumentParser(description="Run offline evaluation")
    parser.add_argument(
        "--dataset", 
        default="evals/datasets/rag_ai_act_v1.jsonl",
        help="Path to evaluation dataset (JSONL format)"
    )
    parser.add_argument(
        "--output-dir", 
        default="evals/reports", 
        help="Output directory for evaluation results"
    )
    parser.add_argument(
        "--use-compliance-pipeline",
        action="store_true",
        help="Use compliance-focused RAG pipeline"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize services
        print("Initializing services...")
        vectorstore_service = VectorStoreService()
        
        # Load AI Act corpus if using compliance pipeline
        if args.use_compliance_pipeline:
            print("Loading AI Act corpus...")
            vectorstore_service.load_ai_act_corpus()
        else:
            vectorstore_service.load_vectorstore()
        
        # Choose evaluation service
        if args.use_compliance_pipeline:
            from src.app.services.rag_pipeline import ComplianceRAGPipeline
            compliance_pipeline = ComplianceRAGPipeline(vectorstore_service)
            evaluation_service = ComplianceEvaluationService(compliance_pipeline)
        else:
            rag_service = RAGService(vectorstore_service)
            evaluation_service = EvaluationService(rag_service)
        
        # Run evaluation
        print(f"Running evaluation on dataset: {args.dataset}")
        report = evaluation_service.run_evaluation(
            dataset_path=args.dataset,
            output_dir=args.output_dir
        )
        
        # Print results
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        print(f"Total questions: {report.total_questions}")
        print(f"Average groundedness: {report.avg_groundedness:.3f}")
        print(f"Average correctness: {report.avg_correctness:.3f}")
        print(f"Passed threshold: {report.passed_threshold}")
        if hasattr(report, 'compliance_metadata'):
            print(f"Compliance focus: {report.compliance_metadata.get('compliance_focus', False)}")
        print("="*50)
        
        # Exit with error code if thresholds not met
        if not report.passed_threshold:
            print("❌ Evaluation failed: Thresholds not met")
            sys.exit(1)
        else:
            print("✅ Evaluation passed: All thresholds met")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error running evaluation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
