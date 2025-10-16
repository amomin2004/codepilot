"""
Quick unit tests for ingestion pipeline.
Run with: pytest test_ingest.py -v
"""

from pathlib import Path
import tempfile
import shutil
from ingest import (
    list_source_files,
    read_text_safely,
    chunk_lines,
    detect_lang_from_ext,
    hash_text,
    make_preview,
    ingest_repo,
    Chunk,
)


def test_list_source_files():
    """Test file discovery with filters."""
    # Create a temp directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create test files
        (root / "main.py").write_text("print('hello')")
        (root / "test.ts").write_text("console.log('hi')")
        (root / "ignore.txt").write_text("should not appear")
        (root / "node_modules").mkdir()
        (root / "node_modules" / "lib.js").write_text("module.exports = {}")
        
        files = list_source_files(root, [".py", ".ts"], ["node_modules"])
        
        assert "main.py" in files
        assert "test.ts" in files
        assert "ignore.txt" not in files
        assert "node_modules/lib.js" not in files


def test_read_text_safely():
    """Test file reading with encoding detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.py"
        path.write_text("def hello():\n    return 'world'", encoding="utf-8")
        
        content = read_text_safely(path)
        assert content is not None
        assert "def hello()" in content


def test_chunk_lines():
    """Test fixed-window chunking."""
    lines = [f"line {i}\n" for i in range(100)]
    
    chunks = chunk_lines(lines, window=20, overlap=5, min_lines=5)
    
    # First chunk: lines 1-20
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 20
    
    # Second chunk: lines 16-35 (overlap of 5)
    assert chunks[1].start_line == 16
    
    # All chunks should have text
    for chunk in chunks:
        assert len(chunk.text) > 0


def test_detect_lang():
    """Test language detection."""
    assert detect_lang_from_ext("main.py") == "python"
    assert detect_lang_from_ext("app.ts") == "typescript"
    assert detect_lang_from_ext("server.js") == "javascript"
    assert detect_lang_from_ext("main.go") == "go"
    assert detect_lang_from_ext("unknown.xyz") == "unknown"


def test_hash_text():
    """Test hashing for deduplication."""
    text1 = "def hello():\n    pass"
    text2 = "def hello():\n    pass"
    text3 = "def world():\n    pass"
    
    hash1 = hash_text(text1)
    hash2 = hash_text(text2)
    hash3 = hash_text(text3)
    
    assert hash1 == hash2  # Same text = same hash
    assert hash1 != hash3  # Different text = different hash
    assert len(hash1) == 16  # Should be truncated to 16 chars


def test_make_preview():
    """Test preview generation."""
    text = "\n".join([f"line {i}" for i in range(50)])
    
    preview = make_preview(text, max_lines=10)
    preview_lines = preview.splitlines()
    
    assert len(preview_lines) <= 10
    assert "line 0" in preview
    assert "line 9" in preview or "line 10" in preview


def test_ingest_repo_integration():
    """Integration test: full pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a mini repo
        (root / "main.py").write_text(
            "\n".join([f"# Line {i}" for i in range(100)])
        )
        (root / "utils.py").write_text(
            "def helper():\n    return True"
        )
        
        chunks, stats = ingest_repo(
            root,
            include_exts=[".py"],
            window=20,
            overlap=5,
            min_lines=5,
        )
        
        assert stats["files_scanned"] == 2
        assert stats["files_read"] == 2
        assert stats["chunks_total"] > 0
        assert len(chunks) == stats["chunks_total"]
        
        # Check chunk structure
        chunk = chunks[0]
        assert chunk.repo == root.name
        assert chunk.lang == "python"
        assert chunk.start_line >= 1
        assert chunk.end_line > chunk.start_line
        assert len(chunk.text) > 0
        assert len(chunk.hash) == 16
        assert len(chunk.preview) > 0


if __name__ == "__main__":
    # Run tests manually
    test_list_source_files()
    test_read_text_safely()
    test_chunk_lines()
    test_detect_lang()
    test_hash_text()
    test_make_preview()
    test_ingest_repo_integration()
    
    print("✅ All tests passed!")

