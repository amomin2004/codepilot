# CodePilot 🔍

> Semantic code search engine: Ask questions in natural language, get relevant code instantly.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**CodePilot** lets you search codebases using natural language queries like *"Where is JWT validation?"* or *"How do we handle database connections?"* instead of grep or keyword search.

## 🚀 Features

- **Semantic search** - Find code by meaning, not just keywords
- **Multi-language support** - Python, TypeScript, JavaScript, Go, Java, and more
- **Fast** - Sub-second search on 10k+ code chunks
- **Local & private** - All embeddings and indexing happen on your machine
- **Line-precise results** - Get exact file paths with line numbers

## 📊 Current Status

**Progress:** Phase 3 Complete (50%) - **Fully Functional API!** 🎉

- ✅ **Phase 1:** Ingestion pipeline (file discovery, chunking, metadata)
- ✅ **Phase 2:** Embeddings & vector index (SentenceTransformers + FAISS)
- ✅ **Phase 3:** Search API (FastAPI server with /ingest and /search endpoints)
- 🔨 **Phase 4:** Web UI (Next.js) - *Next*
- ⏳ **Phase 5:** Evaluation & metrics
- ⏳ **Phase 6:** Docker & polish

## 🏗️ Architecture

```
┌─────────────┐
│   Web UI    │  ← Next.js + Tailwind
└──────┬──────┘
       │
┌──────▼───────┐
│  FastAPI     │  ← Search endpoints
│  Server      │
└──────┬───────┘
       │
┌──────▼───────┐
│   FAISS      │  ← Vector similarity search
│   Index      │
└──────┬───────┘
       │
┌──────▼───────┐
│ Embeddings   │  ← SentenceTransformers (MiniLM-L6-v2)
└──────────────┘
```

## 📁 Project Structure

```
codepilot/
├── api/
│   ├── ingest.py          # Phase 1: File discovery, chunking, metadata
│   ├── embeddings.py      # Phase 2: Text → vectors
│   ├── vector_index.py    # Phase 2: FAISS operations
│   ├── search.py          # Phase 3: Filtering, ranking, result assembly
│   ├── main.py            # Phase 3: FastAPI server
│   ├── cli_ingest.py      # CLI tool for testing
│   └── test_*.py          # Test suite
├── data/                  # Test repositories
├── output/                # Generated chunks & indexes
├── requirements.txt       # Python dependencies
├── ROADMAP.md            # Full development plan
└── API_QUICK_START.md    # API usage guide
```

## 🔧 Installation

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/codepilot.git
cd codepilot

# Install dependencies
pip install -r requirements.txt

# Note: First run will download the embedding model (~80MB)
```

## 🎮 Usage

### Start the API Server

```bash
python api/main.py
```

Server runs on: **http://localhost:8000**

### Quick Test

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Ingest a repository
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "data/fastapi/fastapi"}'

# 3. Search!
curl "http://localhost:8000/search?q=JWT%20validation&k=5"
```

### Interactive API Docs

Visit http://localhost:8000/docs for full API documentation.

## 🧪 Testing

### Test Ingestion (Phase 1)

```bash
python api/test_ingest.py
# ✅ All tests passed!
```

### Test Embeddings & Index (Phase 2)

```bash
python api/test_phase2.py
# ✅ All Phase 2 tests passed!
```

### Test API (Phase 3)

```bash
# Unit tests
python api/test_phase3.py

# Integration tests (requires server running)
python api/main.py  # Terminal 1
python api/test_server.py  # Terminal 2
# ✅ All tests passed!
```

### CLI Ingestion (Optional)

```bash
python api/cli_ingest.py data/fastapi/fastapi
```

## 🎯 Design Decisions

### Why MiniLM-L6-v2?
- **Small:** 80MB model, 384-dimensional embeddings
- **Fast:** ~1000 texts/sec on CPU
- **Quality:** Good for code similarity despite being trained on natural language
- **Local:** No API calls, works offline

### Why FAISS?
- **Exact search:** IndexFlatIP for perfect accuracy
- **Fast:** <5ms search on 10k chunks
- **Scalable:** Can upgrade to approximate search (IVF) for 100k+ chunks
- **Battle-tested:** Used by industry at scale

### Why Fixed-Window Chunking?
- **Simple:** Works for all languages without AST parsing
- **Overlap:** 15-line overlap preserves context across boundaries
- **Configurable:** Window size (80 lines) and overlap easily tuned
- **Future:** Can add AST-based chunking as enhancement

## 📈 Performance

### Achieved (Tested on FastAPI repo - 308 chunks)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Ingestion speed** | 7.5 files/sec | - | ✅ |
| **Search latency (p50)** | ~100ms | <200ms | ✅ |
| **Search latency (p95)** | ~400ms | <400ms | ✅ |
| **Index build** | ~50ms | - | ✅ |
| **Memory usage** | ~350MB for 300 chunks | - | ✅ |

### Example Search Results

```bash
Query: "JWT validation"
Results: 5 relevant chunks
Latency: 173ms
Top result: security/http.py ✓ (correct!)
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) |
| **Embeddings** | SentenceTransformers |
| **Vector Search** | FAISS (CPU) |
| **Storage** | JSONL (metadata) + FAISS index |
| **Frontend** | Next.js + Tailwind *(coming)* |
| **Deployment** | Docker Compose *(coming)* |

## 📚 Documentation

- [API_QUICK_START.md](API_QUICK_START.md) - **Start here!** Quick API guide
- [ROADMAP.md](ROADMAP.md) - Complete 6-phase development plan
- [PROGRESS.md](PROGRESS.md) - Detailed progress tracker
- [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) - Phase 2 summary
- [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md) - Phase 3 summary
- [TODO.md](TODO.md) - Task checklist

## 🧑‍💻 Development

### Running Tests

```bash
# All Phase 1 tests
python api/test_ingest.py

# All Phase 2 tests
python api/test_phase2.py
```

### Code Quality

- Type hints throughout
- Comprehensive docstrings
- Unit + integration tests
- Clean separation of concerns

## 🎓 Use Cases

1. **Onboarding** - New team members finding relevant code
2. **Code review** - Locating similar patterns across the codebase
3. **Refactoring** - Finding all uses of a pattern or concept
4. **Documentation** - Discovering implementation details
5. **Learning** - Exploring unfamiliar codebases

## 🚧 Roadmap

**Completed:**

- [x] Phase 1: Ingestion pipeline
- [x] Phase 2: Embeddings & FAISS index
- [x] Phase 3: FastAPI server with `/ingest` and `/search` endpoints

**Next milestones:**

- [ ] Phase 4: Web UI for search + results (Next.js)
- [ ] Phase 5: Evaluation with precision@k metrics
- [ ] Phase 6: Docker setup + final polish

**Future enhancements:**

- Hybrid search (BM25 + vector)
- AST-based chunking
- Multi-repo support
- Incremental indexing
- IDE extensions

## 🙏 Acknowledgments

- FastAPI for test data
- SentenceTransformers team for the embedding models
- FAISS team for the vector search library

## 📬 Contact

Built by Ali Asgar Momin - Portfolio project demonstrating:
- Semantic search implementation
- Vector embeddings & similarity
- Full-stack development
- System design & architecture
- Test-driven development

---

**Status:** Phase 3 Complete - Fully Functional API! 🎉 | **Next:** Web UI | **MVP Target:** ~10 more hours

