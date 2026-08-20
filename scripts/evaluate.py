import os
import time
import json
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# Dummy dataset for illustration. In reality, load from evaluation/datasets/
eval_data = {
    "question": ["What is LangGraph?", "How does reciprocal rank fusion work?"],
    "answer": ["LangGraph is a library for building stateful multi-actor applications with LLMs.", "RRF is an algorithm that combines rankings from multiple sources."],
    "contexts": [
        ["LangGraph is a library for building stateful, multi-actor applications with LLMs, built on top of LangChain."],
        ["Reciprocal Rank Fusion (RRF) is a method for combining document rankings from multiple information retrieval systems."]
    ],
    "ground_truth": ["A framework for stateful agents.", "A method to merge search rankings."]
}

def run_evaluation():
    print("Starting DeepSearch AI Evaluation...")
    start_time = time.time()
    
    dataset = Dataset.from_dict(eval_data)
    
    # Run Ragas evaluation
    # Note: Requires OPENAI_API_KEY to be set in environment for Ragas evaluator LLM
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY not found. Ragas evaluation requires an LLM provider.")
        return
        
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
    )
    
    end_time = time.time()
    
    print("\n--- Evaluation Results ---")
    print(result)
    print(f"\nEvaluation completed in {end_time - start_time:.2f} seconds.")
    
    # Save results
    os.makedirs("evaluation", exist_ok=True)
    with open("evaluation/latest_results.json", "w") as f:
        # Convert result object to dict for saving
        # In ragas, result acts like a dict
        json.dump(dict(result), f, indent=2)
        
    print("Results saved to evaluation/latest_results.json")

if __name__ == "__main__":
    run_evaluation()
