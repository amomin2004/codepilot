"""
FAISS vector index module for CodePilot.

Handles building, saving, loading, and searching a FAISS index for semantic similarity.
"""

from pathlib import Path
import numpy as np
import faiss
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def build_index(embeddings: np.ndarray, index_type: str = "flat") -> faiss.Index:
    """
    Build a FAISS index from embeddings.
    
    Args:
        embeddings: numpy array of shape (n_chunks, embedding_dim)
        index_type: "flat" for exact search (default), "ivf" for approximate (future)
        
    Returns:
        FAISS index
    """
    if embeddings.shape[0] == 0:
        raise ValueError("Cannot build index from empty embeddings array")
    
    n_chunks, embedding_dim = embeddings.shape
    logger.info(f"Building FAISS index for {n_chunks} chunks with dimension {embedding_dim}")
    
    # Ensure float32 (FAISS requirement)
    embeddings = embeddings.astype('float32')
    
    if index_type == "flat":
        # IndexFlatIP: exact inner product search (works with normalized vectors for cosine)
        index = faiss.IndexFlatIP(embedding_dim)
    else:
        raise ValueError(f"Unsupported index type: {index_type}")
    
    # Add vectors to index
    index.add(embeddings)
    
    logger.info(f"Index built successfully. Total vectors: {index.ntotal}")
    
    return index


def save_index(index: faiss.Index, path: Path | str) -> None:
    """
    Save FAISS index to disk.
    
    Args:
        index: FAISS index to save
        path: file path to save to
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(path))
    logger.info(f"Index saved to: {path}")


def load_index(path: Path | str) -> Optional[faiss.Index]:
    """
    Load FAISS index from disk.
    
    Args:
        path: file path to load from
        
    Returns:
        FAISS index, or None if file doesn't exist
    """
    path = Path(path)
    
    if not path.exists():
        logger.warning(f"Index file not found: {path}")
        return None
    
    index = faiss.read_index(str(path))
    logger.info(f"Index loaded from: {path}. Total vectors: {index.ntotal}")
    
    return index


def search_index(
    index: faiss.Index,
    query_vector: np.ndarray,
    k: int = 5,
    oversample_factor: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Search the FAISS index for similar vectors.
    
    Args:
        index: FAISS index to search
        query_vector: query embedding of shape (embedding_dim,) or (1, embedding_dim)
        k: number of results to return
        oversample_factor: retrieve k * oversample_factor results (for post-filtering)
        
    Returns:
        Tuple of (distances, indices) arrays
        - distances: similarity scores (higher = more similar for inner product)
        - indices: chunk indices in the original embeddings array
    """
    # Ensure correct shape
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)
    
    # Ensure float32
    query_vector = query_vector.astype('float32')
    
    # Oversample for filtering
    k_search = min(k * oversample_factor, index.ntotal)
    
    # Search
    distances, indices = index.search(query_vector, k_search)
    
    # Return flattened results (since we only have 1 query)
    return distances[0], indices[0]


def get_index_stats(index: faiss.Index) -> dict:
    """
    Get statistics about the index.
    
    Args:
        index: FAISS index
        
    Returns:
        Dictionary with stats
    """
    return {
        "total_vectors": index.ntotal,
        "dimension": index.d,
        "is_trained": index.is_trained,
    }

