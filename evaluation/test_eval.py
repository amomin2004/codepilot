#!/usr/bin/env python3
"""
Test script for CodePilot evaluation system.

Tests the evaluation pipeline with a small subset of queries.
"""

import json
import time
import requests
from pathlib import Path
from eval import CodePilotEvaluator


def test_api_connectivity():
    """Test if API server is accessible."""
    print("🔍 Testing API connectivity...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is responding")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


def test_search_functionality():
    """Test basic search functionality."""
    print("🔍 Testing search functionality...")
    
    try:
        response = requests.get(
            "http://localhost:8000/search",
            params={"q": "How do I validate JWT tokens?", "k": 5},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"✅ Search returned {len(results)} results")
            
            if results:
                print("   Top result:")
                top_result = results[0]
                print(f"     Path: {top_result.get('path', 'N/A')}")
                print(f"     Score: {top_result.get('score', 'N/A')}")
                print(f"     Lines: {top_result.get('start_line', 'N/A')}-{top_result.get('end_line', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Search failed: {e}")
        return False


def test_golden_set():
    """Test loading and validating golden set."""
    print("🔍 Testing golden set...")
    
    golden_file = Path("evaluation/goldens.json")
    if not golden_file.exists():
        print(f"❌ Golden set file not found: {golden_file}")
        return False
    
    try:
        with open(golden_file, 'r') as f:
            golden_set = json.load(f)
        
        # Validate structure
        required_fields = ["dataset_name", "queries", "targets"]
        for field in required_fields:
            if field not in golden_set:
                print(f"❌ Missing required field: {field}")
                return False
        
        queries = golden_set["queries"]
        print(f"✅ Golden set loaded: {golden_set['dataset_name']}")
        print(f"   Total queries: {len(queries)}")
        
        # Validate query structure
        if queries:
            first_query = queries[0]
            required_query_fields = ["id", "query", "category", "expected_files"]
            for field in required_query_fields:
                if field not in first_query:
                    print(f"❌ Missing query field: {field}")
                    return False
        
        print("✅ Golden set structure is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in golden set: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading golden set: {e}")
        return False


def test_single_query_evaluation():
    """Test evaluation of a single query."""
    print("🔍 Testing single query evaluation...")
    
    try:
        evaluator = CodePilotEvaluator()
        
        # Create a simple test query
        test_query = {
            "id": "test_001",
            "query": "How do I validate JWT tokens?",
            "category": "authentication",
            "difficulty": "medium",
            "expected_files": ["fastapi/security/oauth2.py", "fastapi/security/http.py"],
            "expected_keywords": ["JWT", "token", "validate"]
        }
        
        result = evaluator.evaluate_query(test_query)
        
        print(f"✅ Query evaluation completed")
        print(f"   Query: {result.query}")
        print(f"   Precision@5: {result.precision_at_5:.3f}")
        print(f"   Precision@10: {result.precision_at_10:.3f}")
        print(f"   Reciprocal Rank: {result.reciprocal_rank:.3f}")
        print(f"   Latency: {result.latency_ms:.1f}ms")
        print(f"   Expected files found: {len(result.expected_files_found)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Single query evaluation failed: {e}")
        return False


def test_evaluation_metrics():
    """Test evaluation metrics calculation."""
    print("🔍 Testing evaluation metrics...")
    
    try:
        evaluator = CodePilotEvaluator()
        
        # Mock some results
        results = [
            {"path": "fastapi/security/oauth2.py", "score": 0.9},
            {"path": "fastapi/security/http.py", "score": 0.8},
            {"path": "fastapi/applications.py", "score": 0.7},
            {"path": "fastapi/routing.py", "score": 0.6},
            {"path": "fastapi/exceptions.py", "score": 0.5}
        ]
        
        expected_files = ["fastapi/security/oauth2.py", "fastapi/security/http.py"]
        
        # Test precision@5
        precision_at_5 = evaluator.calculate_precision_at_k(results, expected_files, 5)
        expected_precision = 1.0  # Both expected files in top 5
        assert abs(precision_at_5 - expected_precision) < 0.001, f"Expected {expected_precision}, got {precision_at_5}"
        
        # Test precision@2
        precision_at_2 = evaluator.calculate_precision_at_k(results, expected_files, 2)
        expected_precision = 1.0  # Both expected files in top 2
        assert abs(precision_at_2 - expected_precision) < 0.001, f"Expected {expected_precision}, got {precision_at_2}"
        
        # Test reciprocal rank
        reciprocal_rank = evaluator.calculate_reciprocal_rank(results, expected_files)
        expected_rr = 1.0  # First expected file is at position 1
        assert abs(reciprocal_rank - expected_rr) < 0.001, f"Expected {expected_rr}, got {reciprocal_rank}"
        
        print("✅ All metrics calculations are correct")
        return True
        
    except Exception as e:
        print(f"❌ Metrics calculation failed: {e}")
        return False


def run_quick_evaluation():
    """Run a quick evaluation with a few queries."""
    print("🔍 Running quick evaluation...")
    
    try:
        # Create a mini golden set for testing
        mini_golden_set = {
            "dataset_name": "CodePilot Mini Test",
            "version": "1.0",
            "description": "Quick test evaluation",
            "repository": "data/fastapi/fastapi",
            "total_queries": 3,
            "categories": {
                "authentication": "Security and authentication",
                "routing": "URL routing"
            },
            "queries": [
                {
                    "id": "mini_001",
                    "category": "authentication",
                    "query": "How do I validate JWT tokens?",
                    "expected_files": ["fastapi/security/oauth2.py"],
                    "expected_keywords": ["JWT", "token"],
                    "difficulty": "medium"
                },
                {
                    "id": "mini_002",
                    "category": "routing",
                    "query": "How do I define API routes?",
                    "expected_files": ["fastapi/routing.py"],
                    "expected_keywords": ["route", "APIRouter"],
                    "difficulty": "easy"
                },
                {
                    "id": "mini_003",
                    "category": "authentication",
                    "query": "Where is HTTP Basic auth implemented?",
                    "expected_files": ["fastapi/security/http.py"],
                    "expected_keywords": ["HTTPBasic", "basic"],
                    "difficulty": "easy"
                }
            ],
            "targets": {
                "precision_at_5": 0.8,
                "precision_at_10": 0.9,
                "mean_reciprocal_rank": 0.7,
                "latency_p50": 200,
                "latency_p95": 500,
                "latency_p99": 1000
            }
        }
        
        evaluator = CodePilotEvaluator()
        summary = evaluator.evaluate_dataset(mini_golden_set)
        
        print(f"✅ Quick evaluation completed")
        print(f"   Queries: {summary.total_queries}")
        print(f"   Precision@5: {summary.precision_at_5:.3f}")
        print(f"   Precision@10: {summary.precision_at_10:.3f}")
        print(f"   Mean Latency: {summary.latency_mean:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick evaluation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 CodePilot Evaluation Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Connectivity", test_api_connectivity),
        ("Search Functionality", test_search_functionality),
        ("Golden Set Loading", test_golden_set),
        ("Single Query Evaluation", test_single_query_evaluation),
        ("Metrics Calculation", test_evaluation_metrics),
        ("Quick Evaluation", run_quick_evaluation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Evaluation system is ready.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Check the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())
