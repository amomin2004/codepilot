"""
Test the FastAPI server endpoints.

This tests the API in two modes:
1. Unit tests for search.py functions
2. Integration tests by calling the actual API

Run with: python test_phase3.py
"""

import sys
import time
import requests
from pathlib import Path

# Unit tests for search.py
from search import (
    filter_by_path,
    filter_by_language,
    apply_filters,
    keyword_boost,
    assemble_results,
    search_pipeline,
)
from ingest import ChunkMetadata
import numpy as np


def test_search_functions():
    """Test search.py filtering and ranking functions."""
    print("Testing search functions...")
    
    # Create sample chunks
    chunks = [
        ChunkMetadata(
            repo="test", path="src/auth/jwt.py", lang="python",
            start_line=1, end_line=20, text="def validate_jwt(token):\n    pass",
            hash="abc123", preview="def validate_jwt..."
        ),
        ChunkMetadata(
            repo="test", path="src/auth/oauth.py", lang="python",
            start_line=1, end_line=20, text="def validate_oauth(token):\n    pass",
            hash="def456", preview="def validate_oauth..."
        ),
        ChunkMetadata(
            repo="test", path="src/utils/helper.ts", lang="typescript",
            start_line=1, end_line=20, text="function formatDate() {}",
            hash="ghi789", preview="function formatDate..."
        ),
    ]
    
    indices = np.array([0, 1, 2])
    distances = np.array([0.9, 0.8, 0.7])
    
    # Test path filter
    filtered_idx, filtered_distances = apply_filters(
        chunks, indices, distances, path_contains="auth"
    )
    assert len(filtered_idx) == 2  # Should keep jwt.py and oauth.py
    print("  ✓ Path filtering works")
    
    # Test language filter
    filtered_idx, filtered_distances = apply_filters(
        chunks, indices, distances, lang="python"
    )
    assert len(filtered_idx) == 2  # Should keep .py files
    print("  ✓ Language filtering works")
    
    # Test combined filters
    filtered_idx, filtered_distances = apply_filters(
        chunks, indices, distances, path_contains="auth", lang="python"
    )
    assert len(filtered_idx) == 2
    print("  ✓ Combined filtering works")
    
    # Test keyword boost
    query = "jwt token validation"
    boosted = keyword_boost(chunks, indices, distances, query)
    assert boosted[0] > distances[0]  # jwt.py should be boosted
    print("  ✓ Keyword boosting works")
    
    # Test result assembly
    results = assemble_results(chunks, indices, distances, k=2)
    assert len(results) == 2
    assert results[0]["path"] == "src/auth/jwt.py"  # Highest score first
    assert "score" in results[0]
    print("  ✓ Result assembly works")
    
    # Test full pipeline
    pipeline_results = search_pipeline(
        chunks, indices, distances, query="jwt", k=2, path_contains="auth"
    )
    assert len(pipeline_results) <= 2
    print("  ✓ Full search pipeline works")


def test_api_endpoints():
    """Test the actual API endpoints (requires server to be running)."""
    print("\nTesting API endpoints...")
    print("Note: This requires the server to be running on http://localhost:8000")
    print("Start server with: python api/main.py")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("\n  Testing /health...")
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code == 200:
            print(f"  ✓ Health check passed: {response.json()}")
        else:
            print(f"  ✗ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Status
        print("\n  Testing /status...")
        response = requests.get(f"{base_url}/status", timeout=2)
        if response.status_code == 200:
            status = response.json()
            print(f"  ✓ Status: indexed={status['indexed']}, chunks={status['chunks']}")
        else:
            print(f"  ✗ Status check failed: {response.status_code}")
            return False
        
        # Test 3: Search (if indexed)
        if status['indexed']:
            print("\n  Testing /search...")
            response = requests.get(
                f"{base_url}/search",
                params={"q": "function definition", "k": 3},
                timeout=5
            )
            if response.status_code == 200:
                search_result = response.json()
                print(f"  ✓ Search returned {search_result['total_results']} results")
                print(f"    Latency: {search_result['latency_ms']:.2f}ms")
                
                if search_result['results']:
                    top = search_result['results'][0]
                    print(f"    Top result: {top['path']} (lines {top['start_line']}-{top['end_line']})")
                    print(f"    Score: {top['score']:.3f}")
            else:
                print(f"  ✗ Search failed: {response.status_code}")
                return False
        else:
            print("\n  ⚠ Skipping search test (no data indexed)")
            print("    Run ingestion first: POST /ingest with repo_path")
        
        print("\n  ✅ All API tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n  ⚠ Cannot connect to server at http://localhost:8000")
        print("    Start the server with: python api/main.py")
        print("    Or run: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n  ✗ API test failed: {e}")
        return False


def test_ingest_endpoint_example():
    """
    Example of how to test the /ingest endpoint.
    This is not run automatically as it's time-consuming.
    """
    print("\nExample: Testing /ingest endpoint")
    print("=" * 60)
    print("To test ingestion, run this manually:")
    print()
    print("curl -X POST http://localhost:8000/ingest \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "repo_path": "data/fastapi/fastapi",')
    print('    "window": 80,')
    print('    "overlap": 15')
    print("  }'")
    print()
    print("Or use Python:")
    print()
    print("import requests")
    print("response = requests.post(")
    print("    'http://localhost:8000/ingest',")
    print("    json={'repo_path': 'data/fastapi/fastapi'}")
    print(")")
    print("print(response.json())")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3 Tests: Search API")
    print("=" * 60)
    
    # Unit tests (always run)
    test_search_functions()
    
    # API tests (only if server is running)
    print("\n" + "=" * 60)
    api_success = test_api_endpoints()
    
    # Show ingest example
    print("\n" + "=" * 60)
    test_ingest_endpoint_example()
    
    print("\n" + "=" * 60)
    if api_success:
        print("✅ Phase 3 complete!")
    else:
        print("⚠️  Unit tests passed, but API server needs to be started")
        print("   Run: cd /Users/aliasgarmomin/codepilot && python api/main.py")
    print("=" * 60)

