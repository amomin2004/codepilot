"""
Search logic module for CodePilot.

Handles filtering, ranking, and result assembly for semantic code search.
"""

from typing import Optional
import numpy as np
from ingest import ChunkMetadata
import re


def filter_by_path(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    path_substring: str,
) -> tuple[list[int], list[ChunkMetadata]]:
    """
    Filter results to only include paths containing a substring.
    
    Args:
        chunks: all chunk metadata
        indices: array of chunk indices from FAISS search
        path_substring: substring to search for in paths (case-insensitive)
        
    Returns:
        Tuple of (filtered_indices, filtered_chunks)
    """
    filtered_indices = []
    filtered_chunks = []
    
    path_lower = path_substring.lower()
    
    for idx in indices:
        chunk = chunks[idx]
        if path_lower in chunk.path.lower():
            filtered_indices.append(idx)
            filtered_chunks.append(chunk)
    
    return filtered_indices, filtered_chunks


def filter_by_language(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    language: str,
) -> tuple[list[int], list[ChunkMetadata]]:
    """
    Filter results to only include a specific language.
    
    Args:
        chunks: all chunk metadata
        indices: array of chunk indices from FAISS search
        language: language to filter by (e.g., "python", "typescript")
        
    Returns:
        Tuple of (filtered_indices, filtered_chunks)
    """
    filtered_indices = []
    filtered_chunks = []
    
    lang_lower = language.lower()
    
    for idx in indices:
        chunk = chunks[idx]
        if chunk.lang.lower() == lang_lower:
            filtered_indices.append(idx)
            filtered_chunks.append(chunk)
    
    return filtered_indices, filtered_chunks


def apply_filters(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    distances: np.ndarray,
    path_contains: Optional[str] = None,
    lang: Optional[str] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Apply multiple filters to search results.
    
    Args:
        chunks: all chunk metadata
        indices: array of chunk indices from FAISS
        distances: array of similarity scores from FAISS
        path_contains: optional path substring filter
        lang: optional language filter
        
    Returns:
        Tuple of (filtered_indices, filtered_distances)
    """
    # Start with all results
    current_indices = list(indices)
    current_distances = list(distances)
    
    # Apply path filter
    if path_contains:
        filtered_pairs = []
        path_lower = path_contains.lower()
        
        for idx, dist in zip(current_indices, current_distances):
            if idx >= len(chunks):
                continue
            chunk = chunks[idx]
            if path_lower in chunk.path.lower():
                filtered_pairs.append((idx, dist))
        
        if filtered_pairs:
            current_indices, current_distances = zip(*filtered_pairs)
            current_indices = list(current_indices)
            current_distances = list(current_distances)
        else:
            current_indices = []
            current_distances = []
    
    # Apply language filter
    if lang and current_indices:
        filtered_pairs = []
        lang_lower = lang.lower()
        
        for idx, dist in zip(current_indices, current_distances):
            if idx >= len(chunks):
                continue
            chunk = chunks[idx]
            if chunk.lang.lower() == lang_lower:
                filtered_pairs.append((idx, dist))
        
        if filtered_pairs:
            current_indices, current_distances = zip(*filtered_pairs)
            current_indices = list(current_indices)
            current_distances = list(current_distances)
        else:
            current_indices = []
            current_distances = []
    
    return np.array(current_indices), np.array(current_distances)


def keyword_boost(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    distances: np.ndarray,
    query: str,
    boost_factor: float = 0.1,
) -> np.ndarray:
    """
    Apply a small boost to results containing exact keyword matches.
    
    Args:
        chunks: all chunk metadata
        indices: array of chunk indices
        distances: array of similarity scores
        query: original query string
        boost_factor: how much to boost scores (default 0.1)
        
    Returns:
        Boosted distances array
    """
    # Extract potential keywords (remove common words, split on whitespace/punctuation)
    stop_words = {'the', 'a', 'an', 'is', 'are', 'how', 'do', 'does', 'what', 'where', 'when', 'i', 'we', 'you'}
    
    # Simple tokenization
    tokens = re.findall(r'\w+', query.lower())
    keywords = [t for t in tokens if len(t) > 2 and t not in stop_words]
    
    if not keywords:
        return distances
    
    boosted_distances = distances.copy()
    
    for i, idx in enumerate(indices):
        if idx >= len(chunks):
            continue
        
        chunk = chunks[idx]
        chunk_text_lower = chunk.text.lower()
        
        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in chunk_text_lower)
        
        if matches > 0:
            # Boost the score (higher distances are better for inner product)
            boosted_distances[i] += boost_factor * matches
    
    return boosted_distances


def assemble_results(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    distances: np.ndarray,
    k: int,
) -> list[dict]:
    """
    Assemble final search results into JSON-serializable format.
    
    Args:
        chunks: all chunk metadata
        indices: array of chunk indices (after filtering)
        distances: array of similarity scores (after filtering/boosting)
        k: number of results to return
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    # Sort by distance (descending - higher is better for inner product)
    sorted_pairs = sorted(zip(distances, indices), reverse=True)
    
    # Take top k
    for dist, idx in sorted_pairs[:k]:
        if idx >= len(chunks):
            continue
        
        chunk = chunks[idx]
        
        result = {
            "repo": chunk.repo,
            "path": chunk.path,
            "lang": chunk.lang,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "preview": chunk.preview,
            "score": float(dist),  # Convert numpy float to Python float
        }
        
        results.append(result)
    
    return results


def search_pipeline(
    chunks: list[ChunkMetadata],
    indices: np.ndarray,
    distances: np.ndarray,
    query: str,
    k: int = 5,
    path_contains: Optional[str] = None,
    lang: Optional[str] = None,
    apply_keyword_boost: bool = True,
) -> list[dict]:
    """
    Complete search pipeline: filter, boost, assemble.
    
    Args:
        chunks: all chunk metadata
        indices: raw indices from FAISS search (oversampled)
        distances: raw distances from FAISS search
        query: original query string
        k: number of results to return
        path_contains: optional path filter
        lang: optional language filter
        apply_keyword_boost: whether to apply keyword boosting
        
    Returns:
        List of result dictionaries (top k, sorted by relevance)
    """
    # Apply filters
    filtered_indices, filtered_distances = apply_filters(
        chunks, indices, distances, path_contains, lang
    )
    
    # If no results after filtering, return empty
    if len(filtered_indices) == 0:
        return []
    
    # Apply keyword boost
    if apply_keyword_boost:
        filtered_distances = keyword_boost(
            chunks, filtered_indices, filtered_distances, query
        )
    
    # Assemble results
    results = assemble_results(chunks, filtered_indices, filtered_distances, k)
    
    return results

