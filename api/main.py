"""
FastAPI server for CodePilot semantic code search.

Provides endpoints for ingestion, search, and status checks.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import time
import logging
from typing import Optional
from datetime import datetime
import numpy as np

from api.ingest import (
    ingest_repo, 
    save_chunks_jsonl, 
    load_chunks_jsonl, 
    ChunkMetadata,
    is_github_url,
    clone_github_repo,
    cleanup_temp_repo,
)
from api.embeddings import embed_texts, embed_single, load_embedding_model
from api.vector_index import build_index, save_index, load_index, search_index
from api.search import search_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CodePilot API",
    description="Semantic code search engine",
    version="1.0.0",
)

# Add CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (loaded on startup)
chunks: list[ChunkMetadata] = []
index = None
last_ingest_time: Optional[datetime] = None

# Paths
CHUNKS_PATH = Path("output/chunks.jsonl")
INDEX_PATH = Path("output/index.faiss")


# ========================
# Request/Response Models
# ========================

class IngestRequest(BaseModel):
    repo_path: str = Field(..., description="Path to repository to ingest")
    include_exts: Optional[list[str]] = Field(None, description="File extensions to include")
    exclude_dirs: Optional[list[str]] = Field(None, description="Directories to exclude")
    window: int = Field(80, description="Chunk window size in lines")
    overlap: int = Field(15, description="Overlap between chunks in lines")
    min_lines: int = Field(10, description="Minimum non-blank lines per chunk")


class IngestResponse(BaseModel):
    success: bool
    files_scanned: int
    files_read: int
    files_skipped: int
    chunks_total: int
    avg_lines_per_chunk: float
    duration_seconds: float


class SearchResponse(BaseModel):
    query: str
    k: int
    total_results: int
    latency_ms: float
    results: list[dict]


class StatusResponse(BaseModel):
    indexed: bool
    chunks: int
    last_ingest: Optional[str] = None
    model_loaded: bool
    index_loaded: bool


# ========================
# Startup/Shutdown
# ========================

@app.on_event("startup")
async def startup_event():
    """Load model and index on startup if they exist."""
    global chunks, index, last_ingest_time
    
    logger.info("Starting CodePilot API...")
    
    # Load embedding model
    logger.info("Loading embedding model...")
    load_embedding_model()
    logger.info("✓ Model loaded")
    
    # Load chunks if available
    if CHUNKS_PATH.exists():
        logger.info(f"Loading chunks from {CHUNKS_PATH}...")
        chunks = load_chunks_jsonl(CHUNKS_PATH)
        logger.info(f"✓ Loaded {len(chunks)} chunks")
        last_ingest_time = datetime.fromtimestamp(CHUNKS_PATH.stat().st_mtime)
    else:
        logger.warning("No chunks file found. Run /ingest first.")
    
    # Load index if available
    if INDEX_PATH.exists():
        logger.info(f"Loading FAISS index from {INDEX_PATH}...")
        index = load_index(INDEX_PATH)
        if index:
            logger.info(f"✓ Index loaded with {index.ntotal} vectors")
        else:
            logger.error("Failed to load index")
    else:
        logger.warning("No index file found. Run /ingest first.")
    
    logger.info("🚀 CodePilot API ready!")


# ========================
# Endpoints
# ========================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "service": "CodePilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/status", response_model=StatusResponse, tags=["General"])
async def status():
    """Get system status and statistics."""
    return StatusResponse(
        indexed=index is not None and len(chunks) > 0,
        chunks=len(chunks),
        last_ingest=last_ingest_time.isoformat() if last_ingest_time else None,
        model_loaded=True,  # Loaded on startup
        index_loaded=index is not None,
    )


@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest(request: IngestRequest):
    """
    Ingest a code repository: discover files, chunk, embed, and build index.
    Supports both local paths and GitHub URLs.
    """
    global chunks, index, last_ingest_time
    
    logger.info(f"Starting ingestion of {request.repo_path}")
    start_time = time.time()
    
    # Check if it's a GitHub URL
    is_github = is_github_url(request.repo_path)
    temp_repo_path = None
    actual_repo_path = request.repo_path
    
    try:
        # If GitHub URL, clone it first
        if is_github:
            logger.info(f"Detected GitHub URL: {request.repo_path}")
            logger.info("Cloning repository (this may take a minute)...")
            temp_repo_path = clone_github_repo(request.repo_path)
            actual_repo_path = str(temp_repo_path)
            logger.info(f"✓ Repository cloned to {actual_repo_path}")
        
        # Step 1: Ingest and chunk
        logger.info("Step 1/3: Ingesting repository...")
        new_chunks, stats = ingest_repo(
            repo_path=actual_repo_path,
            include_exts=request.include_exts,
            exclude_dirs=request.exclude_dirs,
            window=request.window,
            overlap=request.overlap,
            min_lines=request.min_lines,
        )
        
        if not new_chunks:
            raise HTTPException(status_code=400, detail="No chunks created. Check repo path and filters.")
        
        logger.info(f"✓ Created {len(new_chunks)} chunks")
        
        # Step 2: Embed chunks
        logger.info("Step 2/3: Generating embeddings...")
        chunk_texts = [chunk.text for chunk in new_chunks]
        embeddings = embed_texts(chunk_texts, batch_size=32, show_progress=True)
        logger.info(f"✓ Generated {len(embeddings)} embeddings")
        
        # Step 3: Build and save index
        logger.info("Step 3/3: Building FAISS index...")
        new_index = build_index(embeddings)
        
        # Save everything
        logger.info("Saving chunks and index...")
        save_chunks_jsonl(new_chunks, CHUNKS_PATH)
        save_index(new_index, INDEX_PATH)
        
        # Update global state
        chunks = new_chunks
        index = new_index
        last_ingest_time = datetime.now()
        
        duration = time.time() - start_time
        logger.info(f"✓ Ingestion complete in {duration:.2f}s")
        
        return IngestResponse(
            success=True,
            files_scanned=stats["files_scanned"],
            files_read=stats["files_read"],
            files_skipped=stats["files_skipped"],
            chunks_total=stats["chunks_total"],
            avg_lines_per_chunk=stats["avg_lines_per_chunk"],
            duration_seconds=round(duration, 2),
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    finally:
        # Clean up temporary GitHub clone
        if temp_repo_path:
            logger.info("Cleaning up temporary repository...")
            cleanup_temp_repo(temp_repo_path)
            logger.info("✓ Cleanup complete")


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search(
    q: str = Query(..., description="Search query"),
    k: int = Query(5, description="Number of results", ge=1, le=50),
    path_contains: Optional[str] = Query(None, description="Filter by path substring"),
    lang: Optional[str] = Query(None, description="Filter by language (e.g., 'python')"),
):
    """
    Semantic search across indexed code.
    """
    # Check if system is ready
    if not chunks or index is None:
        raise HTTPException(
            status_code=503,
            detail="System not ready. Run /ingest first to index a repository."
        )
    
    logger.info(f"Search query: '{q}' (k={k}, path={path_contains}, lang={lang})")
    start_time = time.time()
    
    try:
        # Step 1: Embed query
        query_vector = embed_single(q)
        
        # Step 2: Search FAISS index (oversample for filtering)
        oversample_factor = 5
        distances, indices = search_index(
            index,
            query_vector,
            k=k,
            oversample_factor=oversample_factor,
        )
        
        # Step 3: Apply filters and assemble results
        results = search_pipeline(
            chunks=chunks,
            indices=indices,
            distances=distances,
            query=q,
            k=k,
            path_contains=path_contains,
            lang=lang,
            apply_keyword_boost=True,
        )
        
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"✓ Found {len(results)} results in {latency_ms:.1f}ms")
        
        return SearchResponse(
            query=q,
            k=k,
            total_results=len(results),
            latency_ms=round(latency_ms, 2),
            results=results,
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ========================
# Timing Middleware
# ========================

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# ========================
# Run Server (for development)
# ========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

