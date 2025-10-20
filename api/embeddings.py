"""
Embeddings module for CodePilot.

Handles loading the sentence transformer model and encoding text into vectors.
Uses local models (no API calls) for privacy and speed.
"""

from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Global model instance (loaded once)
_model: Optional[SentenceTransformer] = None
_model_name = "paraphrase-MiniLM-L3-v2"  # Smaller model: 3 layers vs 6, ~200MB RAM vs ~400MB


def load_embedding_model(model_name: str = _model_name, cache_dir: Optional[Path] = None) -> SentenceTransformer:
    """
    Load the sentence transformer model (singleton pattern).
    
    Args:
        model_name: HuggingFace model identifier
        cache_dir: where to cache model files
        
    Returns:
        Loaded SentenceTransformer model
    """
    global _model
    
    if _model is not None:
        return _model
    
    logger.info(f"Loading embedding model: {model_name}")
    
    kwargs = {}
    if cache_dir:
        kwargs["cache_folder"] = str(cache_dir)
    
    _model = SentenceTransformer(model_name, **kwargs)
    
    # Log model info
    embedding_dim = _model.get_sentence_embedding_dimension()
    logger.info(f"Model loaded. Embedding dimension: {embedding_dim}")
    
    return _model


def get_model() -> SentenceTransformer:
    """
    Get the loaded model (loads if not already loaded).
    
    Returns:
        SentenceTransformer instance
    """
    if _model is None:
        return load_embedding_model()
    return _model


def embed_texts(
    texts: list[str],
    batch_size: int = 32,
    show_progress: bool = False,
    normalize: bool = True,
) -> np.ndarray:
    """
    Encode a list of texts into embeddings.
    
    Args:
        texts: list of text strings to encode
        batch_size: number of texts to process at once
        show_progress: whether to show progress bar
        normalize: whether to L2-normalize vectors (required for cosine similarity)
        
    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.array([])
    
    model = get_model()
    
    # Encode in batches
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
    )
    
    return embeddings


def embed_single(text: str, normalize: bool = True) -> np.ndarray:
    """
    Encode a single text string (optimized for queries).
    
    Args:
        text: text string to encode
        normalize: whether to L2-normalize the vector
        
    Returns:
        numpy array of shape (embedding_dim,)
    """
    model = get_model()
    
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=normalize,
    )
    
    return embedding


def get_embedding_dimension() -> int:
    """
    Get the dimensionality of embeddings from the loaded model.
    
    Returns:
        Embedding dimension (e.g., 384 for MiniLM-L6-v2)
    """
    model = get_model()
    return model.get_sentence_embedding_dimension()


# Simple query cache (optional optimization)
_query_cache: dict[str, np.ndarray] = {}


def embed_query_cached(query: str, normalize: bool = True, max_cache_size: int = 100) -> np.ndarray:
    """
    Encode a query with caching for repeated searches.
    
    Args:
        query: query string
        normalize: whether to L2-normalize
        max_cache_size: maximum number of cached queries
        
    Returns:
        numpy array embedding
    """
    if query in _query_cache:
        return _query_cache[query]
    
    # Encode
    embedding = embed_single(query, normalize=normalize)
    
    # Cache it (with simple size limit)
    if len(_query_cache) >= max_cache_size:
        # Remove oldest entry (simple FIFO)
        _query_cache.pop(next(iter(_query_cache)))
    
    _query_cache[query] = embedding
    
    return embedding


def clear_query_cache():
    """Clear the query cache."""
    _query_cache.clear()

