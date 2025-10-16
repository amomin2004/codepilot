#!/usr/bin/env python3
"""
CodePilot Evaluation Script

Evaluates semantic search performance using a golden test set.
Measures precision@k, latency, and other key metrics.
"""

import json
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests
import numpy as np
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    """Results from a single query evaluation."""
    query_id: str
    query: str
    category: str
    difficulty: str
    results: List[Dict]
    latency_ms: float
    precision_at_5: float
    precision_at_10: float
    reciprocal_rank: float
    expected_files_found: List[str]


@dataclass
class EvaluationSummary:
    """Overall evaluation results."""
    total_queries: int
    precision_at_5: float
    precision_at_10: float
    mean_reciprocal_rank: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_mean: float
    category_breakdown: Dict[str, Dict]
    difficulty_breakdown: Dict[str, Dict]
    target_comparison: Dict[str, Dict]


class CodePilotEvaluator:
    """Evaluates CodePilot semantic search performance."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.results: List[EvaluationResult] = []
    
    def load_golden_set(self, golden_file: Path) -> Dict:
        """Load the golden test set."""
        with open(golden_file, 'r') as f:
            return json.load(f)
    
    def search_api(self, query: str, k: int = 10) -> Tuple[List[Dict], float]:
        """Search via API and measure latency."""
        start_time = time.time()
        
        try:
            response = requests.get(
                f"{self.api_base_url}/search",
                params={"q": query, "k": k},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return data.get("results", []), latency_ms
            
        except requests.exceptions.RequestException as e:
            print(f"API error for query '{query}': {e}")
            return [], (time.time() - start_time) * 1000
    
    def calculate_precision_at_k(self, results: List[Dict], expected_files: List[str], k: int) -> float:
        """Calculate precision@k."""
        if not expected_files:
            return 0.0
        
        top_k_results = results[:k]
        found_files = set()
        
        for result in top_k_results:
            file_path = result.get("path", "")
            if file_path in expected_files:
                found_files.add(file_path)
        
        return len(found_files) / len(expected_files)
    
    def calculate_reciprocal_rank(self, results: List[Dict], expected_files: List[str]) -> float:
        """Calculate reciprocal rank of first relevant result."""
        if not expected_files:
            return 0.0
        
        for i, result in enumerate(results):
            file_path = result.get("path", "")
            if file_path in expected_files:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def evaluate_query(self, query_data: Dict) -> EvaluationResult:
        """Evaluate a single query."""
        query_id = query_data["id"]
        query = query_data["query"]
        category = query_data["category"]
        difficulty = query_data["difficulty"]
        expected_files = query_data["expected_files"]
        
        print(f"Evaluating {query_id}: {query[:50]}...")
        
        # Search with k=10 to get enough results for precision@10
        results, latency_ms = self.search_api(query, k=10)
        
        # Calculate metrics
        precision_at_5 = self.calculate_precision_at_k(results, expected_files, 5)
        precision_at_10 = self.calculate_precision_at_k(results, expected_files, 10)
        reciprocal_rank = self.calculate_reciprocal_rank(results, expected_files)
        
        # Find which expected files were found
        found_files = []
        for result in results:
            file_path = result.get("path", "")
            if file_path in expected_files:
                found_files.append(file_path)
        
        return EvaluationResult(
            query_id=query_id,
            query=query,
            category=category,
            difficulty=difficulty,
            results=results,
            latency_ms=latency_ms,
            precision_at_5=precision_at_5,
            precision_at_10=precision_at_10,
            reciprocal_rank=reciprocal_rank,
            expected_files_found=found_files
        )
    
    def evaluate_dataset(self, golden_set: Dict) -> EvaluationSummary:
        """Evaluate the entire golden dataset."""
        queries = golden_set["queries"]
        print(f"Evaluating {len(queries)} queries...")
        
        self.results = []
        
        for query_data in queries:
            try:
                result = self.evaluate_query(query_data)
                self.results.append(result)
                
                # Print immediate feedback
                status = "✓" if result.precision_at_5 > 0 else "✗"
                print(f"  {status} {result.query_id}: P@5={result.precision_at_5:.2f}, "
                      f"P@10={result.precision_at_10:.2f}, RR={result.reciprocal_rank:.2f}, "
                      f"{result.latency_ms:.1f}ms")
                
            except Exception as e:
                print(f"  ✗ {query_data['id']}: Error - {e}")
                continue
        
        return self.generate_summary(golden_set)
    
    def generate_summary(self, golden_set: Dict) -> EvaluationSummary:
        """Generate evaluation summary."""
        if not self.results:
            raise ValueError("No results to summarize")
        
        # Overall metrics
        total_queries = len(self.results)
        precision_at_5 = statistics.mean([r.precision_at_5 for r in self.results])
        precision_at_10 = statistics.mean([r.precision_at_10 for r in self.results])
        mean_reciprocal_rank = statistics.mean([r.reciprocal_rank for r in self.results])
        
        # Latency metrics
        latencies = [r.latency_ms for r in self.results]
        latency_p50 = np.percentile(latencies, 50)
        latency_p95 = np.percentile(latencies, 95)
        latency_p99 = np.percentile(latencies, 99)
        latency_mean = statistics.mean(latencies)
        
        # Category breakdown
        category_breakdown = {}
        for category in golden_set["categories"].keys():
            cat_results = [r for r in self.results if r.category == category]
            if cat_results:
                category_breakdown[category] = {
                    "count": len(cat_results),
                    "precision_at_5": statistics.mean([r.precision_at_5 for r in cat_results]),
                    "precision_at_10": statistics.mean([r.precision_at_10 for r in cat_results]),
                    "mean_reciprocal_rank": statistics.mean([r.reciprocal_rank for r in cat_results]),
                    "avg_latency": statistics.mean([r.latency_ms for r in cat_results])
                }
        
        # Difficulty breakdown
        difficulty_breakdown = {}
        for difficulty in ["easy", "medium", "hard"]:
            diff_results = [r for r in self.results if r.difficulty == difficulty]
            if diff_results:
                difficulty_breakdown[difficulty] = {
                    "count": len(diff_results),
                    "precision_at_5": statistics.mean([r.precision_at_5 for r in diff_results]),
                    "precision_at_10": statistics.mean([r.precision_at_10 for r in diff_results]),
                    "mean_reciprocal_rank": statistics.mean([r.reciprocal_rank for r in diff_results]),
                    "avg_latency": statistics.mean([r.latency_ms for r in diff_results])
                }
        
        # Target comparison
        targets = golden_set["targets"]
        target_comparison = {
            "precision_at_5": {
                "target": targets["precision_at_5"],
                "actual": precision_at_5,
                "met": precision_at_5 >= targets["precision_at_5"]
            },
            "precision_at_10": {
                "target": targets["precision_at_10"],
                "actual": precision_at_10,
                "met": precision_at_10 >= targets["precision_at_10"]
            },
            "mean_reciprocal_rank": {
                "target": targets["mean_reciprocal_rank"],
                "actual": mean_reciprocal_rank,
                "met": mean_reciprocal_rank >= targets["mean_reciprocal_rank"]
            },
            "latency_p50": {
                "target": targets["latency_p50"],
                "actual": latency_p50,
                "met": latency_p50 <= targets["latency_p50"]
            },
            "latency_p95": {
                "target": targets["latency_p95"],
                "actual": latency_p95,
                "met": latency_p95 <= targets["latency_p95"]
            },
            "latency_p99": {
                "target": targets["latency_p99"],
                "actual": latency_p99,
                "met": latency_p99 <= targets["latency_p99"]
            }
        }
        
        return EvaluationSummary(
            total_queries=total_queries,
            precision_at_5=precision_at_5,
            precision_at_10=precision_at_10,
            mean_reciprocal_rank=mean_reciprocal_rank,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            latency_mean=latency_mean,
            category_breakdown=category_breakdown,
            difficulty_breakdown=difficulty_breakdown,
            target_comparison=target_comparison
        )
    
    def print_summary(self, summary: EvaluationSummary):
        """Print evaluation summary."""
        print("\n" + "="*80)
        print("🎯 CodePilot Evaluation Results")
        print("="*80)
        
        # Overall metrics
        print(f"\n📊 Overall Performance:")
        print(f"  Total Queries:     {summary.total_queries}")
        print(f"  Precision@5:       {summary.precision_at_5:.3f}")
        print(f"  Precision@10:      {summary.precision_at_10:.3f}")
        print(f"  Mean Reciprocal Rank: {summary.mean_reciprocal_rank:.3f}")
        
        print(f"\n⚡ Latency (ms):")
        print(f"  P50:  {summary.latency_p50:.1f}")
        print(f"  P95:  {summary.latency_p95:.1f}")
        print(f"  P99:  {summary.latency_p99:.1f}")
        print(f"  Mean: {summary.latency_mean:.1f}")
        
        # Target comparison
        print(f"\n🎯 Target Comparison:")
        for metric, comparison in summary.target_comparison.items():
            status = "✅" if comparison["met"] else "❌"
            print(f"  {status} {metric}: {comparison['actual']:.3f} (target: {comparison['target']:.3f})")
        
        # Category breakdown
        print(f"\n📁 Performance by Category:")
        for category, metrics in summary.category_breakdown.items():
            print(f"  {category}:")
            print(f"    Queries: {metrics['count']}")
            print(f"    P@5: {metrics['precision_at_5']:.3f}, P@10: {metrics['precision_at_10']:.3f}")
            print(f"    MRR: {metrics['mean_reciprocal_rank']:.3f}, Latency: {metrics['avg_latency']:.1f}ms")
        
        # Difficulty breakdown
        print(f"\n🎚️ Performance by Difficulty:")
        for difficulty, metrics in summary.difficulty_breakdown.items():
            print(f"  {difficulty}:")
            print(f"    Queries: {metrics['count']}")
            print(f"    P@5: {metrics['precision_at_5']:.3f}, P@10: {metrics['precision_at_10']:.3f}")
            print(f"    MRR: {metrics['mean_reciprocal_rank']:.3f}, Latency: {metrics['avg_latency']:.1f}ms")
    
    def save_detailed_results(self, output_file: Path):
        """Save detailed results to JSON file."""
        detailed_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "individual_results": [
                {
                    "query_id": r.query_id,
                    "query": r.query,
                    "category": r.category,
                    "difficulty": r.difficulty,
                    "precision_at_5": r.precision_at_5,
                    "precision_at_10": r.precision_at_10,
                    "reciprocal_rank": r.reciprocal_rank,
                    "latency_ms": r.latency_ms,
                    "expected_files_found": r.expected_files_found,
                    "top_5_results": [
                        {
                            "path": result.get("path", ""),
                            "score": result.get("score", 0),
                            "lang": result.get("lang", ""),
                            "start_line": result.get("start_line", 0),
                            "end_line": result.get("end_line", 0)
                        }
                        for result in r.results[:5]
                    ]
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")


def main():
    """Run the evaluation."""
    print("🚀 Starting CodePilot Evaluation")
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server at http://localhost:8000")
        print("   Make sure the server is running: python api/main.py")
        return
    
    # Load golden set
    golden_file = Path("evaluation/goldens.json")
    if not golden_file.exists():
        print(f"❌ Golden set file not found: {golden_file}")
        return
    
    evaluator = CodePilotEvaluator()
    golden_set = evaluator.load_golden_set(golden_file)
    
    print(f"📋 Loaded golden set: {golden_set['dataset_name']}")
    print(f"   Repository: {golden_set['repository']}")
    print(f"   Total queries: {golden_set['total_queries']}")
    
    # Run evaluation
    summary = evaluator.evaluate_dataset(golden_set)
    
    # Print results
    evaluator.print_summary(summary)
    
    # Save detailed results
    output_file = Path("evaluation/results.json")
    evaluator.save_detailed_results(output_file)
    
    # Overall assessment
    targets_met = sum(1 for comp in summary.target_comparison.values() if comp["met"])
    total_targets = len(summary.target_comparison)
    
    print(f"\n🏆 Overall Assessment:")
    print(f"   Targets Met: {targets_met}/{total_targets}")
    
    if targets_met == total_targets:
        print("   🎉 All targets achieved! Excellent performance!")
    elif targets_met >= total_targets * 0.8:
        print("   ✅ Most targets achieved. Good performance!")
    else:
        print("   ⚠️  Some targets missed. Consider optimizations.")


if __name__ == "__main__":
    main()
