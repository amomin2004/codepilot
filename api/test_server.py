"""
Quick server test script.
Tests the API with sample data from the FastAPI repo.

Usage:
    1. Start server: python main.py (in another terminal)
    2. Run this: python test_server.py
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_status():
    """Test status endpoint."""
    print("\nTesting /status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
    return response.status_code == 200, data


def test_ingest():
    """Test ingest endpoint with FastAPI repo."""
    print("\nTesting /ingest...")
    print("  (This may take 10-30 seconds...)")
    
    payload = {
        "repo_path": "data/fastapi/fastapi",
        "window": 80,
        "overlap": 15,
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/ingest", json=payload, timeout=120)
    duration = time.time() - start
    
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Success: {data['success']}")
        print(f"  Files scanned: {data['files_scanned']}")
        print(f"  Files read: {data['files_read']}")
        print(f"  Chunks created: {data['chunks_total']}")
        print(f"  Avg lines per chunk: {data['avg_lines_per_chunk']}")
        print(f"  Duration: {data['duration_seconds']}s (API) / {duration:.2f}s (total)")
        return True, data
    else:
        print(f"  Error: {response.text}")
        return False, None


def test_search(query: str, k: int = 5, **filters):
    """Test search endpoint."""
    print(f"\nTesting /search with query: '{query}'")
    
    params = {"q": query, "k": k}
    params.update(filters)
    
    start = time.time()
    response = requests.get(f"{BASE_URL}/search", params=params)
    duration = time.time() - start
    
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Query: {data['query']}")
        print(f"  Results: {data['total_results']}")
        print(f"  Latency: {data['latency_ms']}ms (API) / {duration*1000:.2f}ms (total)")
        
        if data['results']:
            print(f"\n  Top 3 results:")
            for i, result in enumerate(data['results'][:3], 1):
                print(f"    {i}. {result['path']} (lines {result['start_line']}-{result['end_line']})")
                print(f"       Score: {result['score']:.3f} | Lang: {result['lang']}")
                preview = result['preview'].strip().split('\n')[0][:60]
                print(f"       Preview: {preview}...")
        
        return True, data
    else:
        print(f"  Error: {response.text}")
        return False, None


def run_full_test():
    """Run complete test suite."""
    print("=" * 70)
    print("CodePilot API - Full Integration Test")
    print("=" * 70)
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Health check failed!")
        return False
    
    # Test 2: Status
    success, status_data = test_status()
    if not success:
        print("\n❌ Status check failed!")
        return False
    
    # Test 3: Ingest (if not already indexed)
    if not status_data.get('indexed'):
        print("\n📥 Repository not indexed. Running ingestion...")
        success, ingest_data = test_ingest()
        if not success:
            print("\n❌ Ingestion failed!")
            return False
    else:
        print(f"\n✓ Repository already indexed ({status_data['chunks']} chunks)")
    
    # Test 4: Multiple searches
    test_queries = [
        ("How do I validate JWT tokens?", {}),
        ("WebSocket connection handling", {}),
        ("dependency injection", {"lang": "python"}),
        ("middleware", {"path_contains": "fastapi"}),
    ]
    
    print("\n" + "=" * 70)
    print("Running Search Tests")
    print("=" * 70)
    
    for query, filters in test_queries:
        success, _ = test_search(query, k=5, **filters)
        if not success:
            print(f"\n❌ Search failed for: {query}")
            return False
        time.sleep(0.5)  # Brief pause between searches
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    
    # Final status
    _, final_status = test_status()
    print("\nFinal system status:")
    print(f"  Indexed: {final_status['indexed']}")
    print(f"  Total chunks: {final_status['chunks']}")
    print(f"  Model loaded: {final_status['model_loaded']}")
    print(f"  Index loaded: {final_status['index_loaded']}")
    
    return True


if __name__ == "__main__":
    try:
        success = run_full_test()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Make sure the server is running:")
        print("   cd /Users/aliasgarmomin/codepilot && python api/main.py")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)

