from pathlib import Path
import os
import hashlib
import json
from typing import NamedTuple
import chardet


# ========================
# File Discovery
# ========================

def list_source_files(root: str | Path, include_exts: list[str], exclude_dirs: list[str]) -> list[str]:
    """
    Walk a repo and return paths to source files matching the criteria.
    
    Args:
        root: absolute/relative path to the repo folder
        include_exts: list of extensions to include, e.g. [".py", ".ts", ".js"]
        exclude_dirs: list of directories to exclude, e.g. ["node_modules", "dist"]
        
    Returns:
        List of relative file paths from root, sorted for determinism
    """
    absolutePath = Path(root).resolve()
    if not absolutePath.is_dir():
        raise ValueError(f"Root path is not a directory: {absolutePath}")

    exclude_dirs = set(exclude_dirs)
    include_exts = set((e if e.startswith(".") else f".{e}").lower() for e in include_exts)

    collected_files = []

    for dirpath, dirnames, filenames in os.walk(absolutePath):
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude_dirs and not (Path(dirpath) / d).is_symlink()
        ]

        for file in filenames:

            full_path = Path(dirpath) / file

            if full_path.is_symlink():
                continue

            if full_path.suffix.lower() not in include_exts:
                continue

            if (".min." in file or file in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock"}):
                continue

            try:
                relative_path = full_path.relative_to(absolutePath)
            except ValueError:
                continue

            collected_files.append(relative_path.as_posix())

    return sorted(set(collected_files))


# ========================
# File Reading
# ========================

def read_text_safely(path: Path, max_size_mb: float = 5.0) -> str | None:
    """
    Read a text file with encoding detection and error handling.
    
    Args:
        path: absolute path to file
        max_size_mb: skip files larger than this (MB)
        
    Returns:
        File contents as string, or None if unreadable/too large
    """
    try:
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return None
        
        # Try UTF-8 first (fast path for most source code)
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pass
        
        # Fall back to encoding detection
        raw = path.read_bytes()
        detected = chardet.detect(raw)
        encoding = detected.get("encoding")
        
        if not encoding or detected.get("confidence", 0) < 0.7:
            # Try common fallbacks
            for enc in ["latin-1", "cp1252"]:
                try:
                    return raw.decode(enc)
                except (UnicodeDecodeError, LookupError):
                    continue
            return None
        
        return raw.decode(encoding, errors="replace")
        
    except Exception:
        return None


# ========================
# Language Detection
# ========================

def detect_lang_from_ext(path: str) -> str:
    """
    Map file extension to language identifier.
    
    Args:
        path: file path (relative or absolute)
        
    Returns:
        Language string like "python", "typescript", "javascript", "unknown"
    """
    ext = Path(path).suffix.lower()
    
    lang_map = {
        ".py": "python",
        ".pyi": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".go": "go",
        ".java": "java",
        ".kt": "kotlin",
        ".rs": "rust",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".scala": "scala",
        ".sh": "shell",
        ".bash": "shell",
        ".zsh": "shell",
        ".sql": "sql",
        ".r": "r",
        ".m": "matlab",
        ".lua": "lua",
    }
    
    return lang_map.get(ext, "unknown")


# ========================
# Chunking
# ========================

class Chunk(NamedTuple):
    """Represents a code chunk with line boundaries."""
    text: str
    start_line: int
    end_line: int


def chunk_lines(lines: list[str], window: int = 80, overlap: int = 15, min_lines: int = 10) -> list[Chunk]:
    """
    Split lines into overlapping fixed-size windows.
    
    Args:
        lines: list of text lines (with or without newlines)
        window: number of lines per chunk
        overlap: number of lines to overlap between chunks
        min_lines: skip chunks with fewer non-blank lines than this
        
    Returns:
        List of Chunk objects with text and line boundaries (1-based, inclusive)
    """
    if not lines:
        return []
    
    chunks = []
    total = len(lines)
    stride = window - overlap
    
    if stride <= 0:
        raise ValueError(f"overlap ({overlap}) must be less than window ({window})")
    
    start = 0
    while start < total:
        end = min(start + window, total)
        chunk_lines_slice = lines[start:end]
        
        # Check if chunk has enough non-blank content
        non_blank = sum(1 for line in chunk_lines_slice if line.strip())
        if non_blank >= min_lines:
            text = "".join(chunk_lines_slice)
            chunks.append(Chunk(
                text=text,
                start_line=start + 1,  # 1-based
                end_line=end  # inclusive
            ))
        
        # Move to next window
        start += stride
        
        # If we've reached the end exactly, don't create an empty trailing chunk
        if end >= total:
            break
    
    return chunks


# ========================
# Utilities
# ========================

def hash_text(text: str) -> str:
    """
    Create a deterministic hash for deduplication.
    
    Args:
        text: input string
        
    Returns:
        SHA256 hex digest (first 16 chars for brevity)
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def make_preview(text: str, max_lines: int = 12) -> str:
    """
    Extract first N lines for quick display.
    
    Args:
        text: full chunk text
        max_lines: number of lines to include
        
    Returns:
        Truncated text (preserves newlines)
    """
    lines = text.splitlines(keepends=True)
    preview_lines = lines[:max_lines]
    return "".join(preview_lines)


# ========================
# Main Ingestion
# ========================

class ChunkMetadata(NamedTuple):
    """Complete metadata for a code chunk."""
    repo: str
    path: str
    lang: str
    start_line: int
    end_line: int
    text: str
    hash: str
    preview: str


def ingest_repo(
    repo_path: str | Path,
    include_exts: list[str] | None = None,
    exclude_dirs: list[str] | None = None,
    window: int = 80,
    overlap: int = 15,
    min_lines: int = 10,
    max_file_mb: float = 5.0,
) -> tuple[list[ChunkMetadata], dict]:
    """
    Main ingestion pipeline: discover files → read → chunk → create metadata.
    
    Args:
        repo_path: path to repository root
        include_exts: file extensions to process (default: common code extensions)
        exclude_dirs: directories to skip (default: common build/cache dirs)
        window: chunk size in lines
        overlap: overlapping lines between chunks
        min_lines: minimum non-blank lines per chunk
        max_file_mb: skip files larger than this
        
    Returns:
        Tuple of (list of ChunkMetadata, stats dict)
    """
    # Defaults
    if include_exts is None:
        include_exts = [".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".cpp", ".c", ".rb", ".php"]
    
    if exclude_dirs is None:
        exclude_dirs = [
            ".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv",
            ".mypy_cache", ".pytest_cache", ".tox", "target", ".next", "out",
            "coverage", ".cache", "vendor"
        ]
    
    repo_path = Path(repo_path).resolve()
    repo_name = repo_path.name
    
    # Discover files
    files = list_source_files(repo_path, include_exts, exclude_dirs)
    
    # Stats tracking
    stats = {
        "files_scanned": len(files),
        "files_read": 0,
        "files_skipped": 0,
        "chunks_total": 0,
        "total_lines": 0,
    }
    
    all_chunks: list[ChunkMetadata] = []
    seen_hashes: set[str] = set()
    
    for rel_path in files:
        full_path = repo_path / rel_path
        
        # Read file
        content = read_text_safely(full_path, max_size_mb=max_file_mb)
        if content is None:
            stats["files_skipped"] += 1
            continue
        
        stats["files_read"] += 1
        
        # Split into lines (preserve newlines for reconstruction)
        lines = content.splitlines(keepends=True)
        stats["total_lines"] += len(lines)
        
        # Detect language
        lang = detect_lang_from_ext(rel_path)
        
        # Chunk the file
        chunks = chunk_lines(lines, window=window, overlap=overlap, min_lines=min_lines)
        
        for chunk in chunks:
            chunk_hash = hash_text(chunk.text)
            
            # Deduplicate
            if chunk_hash in seen_hashes:
                continue
            seen_hashes.add(chunk_hash)
            
            # Create metadata
            metadata = ChunkMetadata(
                repo=repo_name,
                path=rel_path,
                lang=lang,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                text=chunk.text,
                hash=chunk_hash,
                preview=make_preview(chunk.text, max_lines=12),
            )
            
            all_chunks.append(metadata)
            stats["chunks_total"] += 1
    
    # Calculate average
    if stats["chunks_total"] > 0:
        stats["avg_lines_per_chunk"] = round(stats["total_lines"] / stats["chunks_total"], 1)
    else:
        stats["avg_lines_per_chunk"] = 0
    
    return all_chunks, stats


# ========================
# Persistence
# ========================

def save_chunks_jsonl(chunks: list[ChunkMetadata], output_path: str | Path) -> None:
    """
    Save chunks to JSONL format (one JSON object per line).
    
    Args:
        chunks: list of chunk metadata
        output_path: where to write the file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            json_obj = {
                "repo": chunk.repo,
                "path": chunk.path,
                "lang": chunk.lang,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "text": chunk.text,
                "hash": chunk.hash,
                "preview": chunk.preview,
            }
            f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")


def load_chunks_jsonl(input_path: str | Path) -> list[ChunkMetadata]:
    """
    Load chunks from JSONL format.
    
    Args:
        input_path: path to JSONL file
        
    Returns:
        List of ChunkMetadata objects
    """
    input_path = Path(input_path)
    if not input_path.exists():
        return []
    
    chunks = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            chunks.append(ChunkMetadata(
                repo=obj["repo"],
                path=obj["path"],
                lang=obj["lang"],
                start_line=obj["start_line"],
                end_line=obj["end_line"],
                text=obj["text"],
                hash=obj["hash"],
                preview=obj["preview"],
            ))
    
    return chunks