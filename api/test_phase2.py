"""
Test embeddings and vector index modules.
Run with: python test_phase2.py
"""

import tempfile
from pathlib import Path
import numpy as np

# Note: These will download the model on first run (~80MB)
from embeddings import (
    load_embedding_model,
    embed_texts,
    embed_single,
    get_embedding_dimension,
    embed_query_cached,
)
from vector_index import (
    build_index,
    save_index,
    load_index,
    search_index,
    get_index_stats,
)


def test_embeddings():
    """Test basic embedding functionality."""
    print("Testing embeddings module...")
    
    # Load model
    model = load_embedding_model()
    assert model is not None
    
    # Check dimension
    dim = get_embedding_dimension()
    print(f"  ✓ Model loaded, embedding dimension: {dim}")
    assert dim == 384  # MiniLM-L6-v2 uses 384 dimensions
    
    # Encode single text
    text = "def authenticate(token: str) -> bool:"
    embedding = embed_single(text)
    assert embedding.shape == (384,)
    assert 0.99 < np.linalg.norm(embedding) <= 1.01  # Should be normalized
    print(f"  ✓ Single text encoded, shape: {embedding.shape}, norm: {np.linalg.norm(embedding):.3f}")
    
    # Encode batch
    texts = [
        "def authenticate(token: str) -> bool:",
        "function validateJWT(token) {",
        "class UserAuthenticator:",
        "const middleware = (req, res, next) =>",
    ]
    embeddings = embed_texts(texts)
    assert embeddings.shape == (4, 384)
    print(f"  ✓ Batch encoded, shape: {embeddings.shape}")
    
    # Check similarity (auth-related texts should be similar)
    sim1 = np.dot(embeddings[0], embeddings[1])  # Both auth functions
    sim2 = np.dot(embeddings[0], embeddings[3])  # Auth vs generic middleware
    assert sim1 > sim2  # Auth functions should be more similar
    print(f"  ✓ Similarity check: auth-auth={sim1:.3f} > auth-middleware={sim2:.3f}")
    
    # Test caching
    cached = embed_query_cached("test query")
    cached2 = embed_query_cached("test query")
    assert np.array_equal(cached, cached2)
    print(f"  ✓ Query caching works")


def test_vector_index():
    """Test FAISS index operations."""
    print("\nTesting vector index module...")
    
    # Create dummy embeddings
    n_chunks = 100
    dim = 384
    embeddings = np.random.randn(n_chunks, dim).astype('float32')
    # Normalize for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Build index
    index = build_index(embeddings)
    assert index.ntotal == n_chunks
    print(f"  ✓ Index built with {index.ntotal} vectors")
    
    # Get stats
    stats = get_index_stats(index)
    assert stats["total_vectors"] == n_chunks
    assert stats["dimension"] == dim
    print(f"  ✓ Index stats: {stats}")
    
    # Search
    query = embeddings[0]  # Use first embedding as query
    distances, indices = search_index(index, query, k=5)
    assert len(distances) >= 5
    assert len(indices) >= 5
    assert indices[0] == 0  # Should match itself as top result
    print(f"  ✓ Search returned {len(indices)} results, top index: {indices[0]}")
    
    # Save and load
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test.index"
        
        save_index(index, index_path)
        assert index_path.exists()
        print(f"  ✓ Index saved")
        
        loaded = load_index(index_path)
        assert loaded is not None
        assert loaded.ntotal == n_chunks
        print(f"  ✓ Index loaded, vectors: {loaded.ntotal}")


def test_integration():
    """Test end-to-end: embed and search."""
    print("\nTesting integration (embed + index + search)...")
    
    # Sample code chunks
    chunks = [
        "def validate_jwt_token(token: str) -> dict:\n    decoded = jwt.decode(token)\n    return decoded",
        "function authenticateUser(username, password) {\n    return db.checkCredentials(username, password);\n}",
        "class DatabaseConnection:\n    def __init__(self, host, port):\n        self.host = host",
        "const fetchUsers = async () => {\n    const response = await api.get('/users');\n    return response.data;\n}",
        "def parse_config_file(path: str) -> dict:\n    with open(path) as f:\n        return json.load(f)",
    ]
    
    # Embed chunks
    embeddings = embed_texts(chunks)
    print(f"  ✓ Embedded {len(chunks)} chunks")
    
    # Build index
    index = build_index(embeddings)
    print(f"  ✓ Built index with {index.ntotal} vectors")
    
    # Query 1: "JWT validation"
    query1 = "How do I validate JWT tokens?"
    query_vec1 = embed_single(query1)
    distances1, indices1 = search_index(index, query_vec1, k=3)
    
    top_result_idx = indices1[0]
    print(f"  ✓ Query 1: '{query1}'")
    print(f"    Top result (score={distances1[0]:.3f}): {chunks[top_result_idx][:60]}...")
    assert top_result_idx == 0  # Should match JWT validation chunk
    
    # Query 2: "database connection"
    query2 = "How do I connect to a database?"
    query_vec2 = embed_single(query2)
    distances2, indices2 = search_index(index, query_vec2, k=3)
    
    top_result_idx2 = indices2[0]
    print(f"  ✓ Query 2: '{query2}'")
    print(f"    Top result (score={distances2[0]:.3f}): {chunks[top_result_idx2][:60]}...")
    # Should match DatabaseConnection chunk (index 2) or authenticateUser (has 'db')
    
    print(f"\n  ✓ Integration test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 2 Tests: Embeddings + Vector Index")
    print("=" * 60)
    print("Note: First run will download model (~80MB)\n")
    
    test_embeddings()
    test_vector_index()
    test_integration()
    
    print("\n" + "=" * 60)
    print("✅ All Phase 2 tests passed!")
    print("=" * 60)

