#!/usr/bin/env python3
"""
Simple CLI to test ingestion pipeline.

Usage:
    python cli_ingest.py /path/to/repo
"""

import sys
import time
from pathlib import Path
from ingest import ingest_repo, save_chunks_jsonl


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_ingest.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print(f"🔍 Ingesting repo: {repo_path}")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run ingestion
    chunks, stats = ingest_repo(
        repo_path=repo_path,
        window=80,
        overlap=15,
        min_lines=10,
    )
    
    elapsed = time.time() - start_time
    
    # Print stats
    print(f"\n✅ Ingestion complete in {elapsed:.2f}s\n")
    print(f"Files scanned:        {stats['files_scanned']}")
    print(f"Files read:           {stats['files_read']}")
    print(f"Files skipped:        {stats['files_skipped']}")
    print(f"Total lines:          {stats['total_lines']}")
    print(f"Chunks created:       {stats['chunks_total']}")
    print(f"Avg lines per chunk:  {stats['avg_lines_per_chunk']}")
    
    # Save to JSONL
    output_path = Path("output") / "chunks.jsonl"
    save_chunks_jsonl(chunks, output_path)
    print(f"\n💾 Saved chunks to: {output_path}")
    
    # Show a sample chunk
    if chunks:
        print(f"\n📄 Sample chunk:")
        print("=" * 60)
        sample = chunks[0]
        print(f"Repo:   {sample.repo}")
        print(f"Path:   {sample.path}")
        print(f"Lang:   {sample.lang}")
        print(f"Lines:  {sample.start_line}-{sample.end_line}")
        print(f"Hash:   {sample.hash}")
        print(f"\nPreview:\n{sample.preview[:300]}...")


if __name__ == "__main__":
    main()

