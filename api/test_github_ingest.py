"""
Test script for GitHub URL ingestion functionality.
"""

import sys
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.ingest import (
    is_github_url,
    normalize_github_url,
    clone_github_repo,
    cleanup_temp_repo,
)


def test_is_github_url():
    """Test GitHub URL detection."""
    print("Testing GitHub URL detection...")
    
    test_cases = [
        ("https://github.com/facebook/react", True),
        ("http://github.com/user/repo", True),
        ("https:/github.com/user/repo", True),  # Malformed (one slash)
        ("git@github.com:user/repo.git", True),
        ("github.com/user/repo", True),
        ("/path/to/local/repo", False),
        ("data/fastapi/fastapi", False),
        ("C:\\Users\\repo", False),
    ]
    
    for url, expected in test_cases:
        result = is_github_url(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {url}: {result} (expected: {expected})")
    
    print()


def test_normalize_github_url():
    """Test GitHub URL normalization."""
    print("Testing GitHub URL normalization...")
    
    test_cases = [
        ("https://github.com/facebook/react", "https://github.com/facebook/react.git"),
        ("http://github.com/user/repo", "https://github.com/user/repo.git"),
        ("https:/github.com/user/repo", "https://github.com/user/repo.git"),  # Malformed
        ("git@github.com:user/repo.git", "https://github.com/user/repo.git"),
        ("github.com/user/repo", "https://github.com/user/repo.git"),
        ("https://github.com/user/repo/", "https://github.com/user/repo.git"),
        ("https://github.com/user/repo.git", "https://github.com/user/repo.git"),
    ]
    
    for url, expected in test_cases:
        result = normalize_github_url(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {url}")
        print(f"      → {result}")
        if result != expected:
            print(f"      Expected: {expected}")
    
    print()


def test_clone_github_repo():
    """Test actual GitHub repository cloning (requires internet)."""
    print("Testing GitHub repository cloning...")
    print("  This will clone a small test repository...")
    
    # Use a very small public repo for testing
    test_repo = "https://github.com/octocat/Hello-World"
    
    try:
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="codepilot_test_"))
        print(f"  Temp directory: {temp_dir}")
        
        # Clone
        print(f"  Cloning {test_repo}...")
        repo_path = clone_github_repo(test_repo, temp_dir)
        print(f"  ✓ Cloned to: {repo_path}")
        
        # Verify clone
        if repo_path.exists() and repo_path.is_dir():
            files = list(repo_path.iterdir())
            print(f"  ✓ Repository contains {len(files)} items")
            print(f"    Files: {[f.name for f in files[:5]]}")
        else:
            print("  ✗ Clone directory not found!")
        
        # Cleanup
        print(f"  Cleaning up...")
        cleanup_temp_repo(repo_path)
        
        if not repo_path.exists():
            print("  ✓ Cleanup successful")
        else:
            print("  ✗ Cleanup failed - directory still exists")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()


def test_integration():
    """Test the complete flow."""
    print("Testing complete integration...")
    
    # This would test with the actual API
    print("  (This would require the API to be running)")
    print("  To test manually:")
    print("    1. Start API: python api/main.py")
    print("    2. Run: curl -X POST http://localhost:8000/ingest \\")
    print("         -H 'Content-Type: application/json' \\")
    print("         -d '{\"repo_path\": \"https://github.com/octocat/Hello-World\"}'")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Ingestion Test Suite")
    print("=" * 60)
    print()
    
    test_is_github_url()
    test_normalize_github_url()
    test_clone_github_repo()
    test_integration()
    
    print("=" * 60)
    print("Test suite complete!")
    print("=" * 60)

