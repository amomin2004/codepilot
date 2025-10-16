# CodePilot — Development Roadmap

## ✅ Phase 1: Ingestion (COMPLETE)

### Completed Components
- [x] `list_source_files` — File discovery with exclusions
- [x] `read_text_safely` — Encoding detection & error handling
- [x] `chunk_lines` — Fixed-window chunking with overlap
- [x] `detect_lang_from_ext` — Language detection
- [x] `hash_text` — Content hashing for deduplication
- [x] `make_preview` — Preview generation
- [x] `ingest_repo` — Main orchestrator
- [x] `save_chunks_jsonl` / `load_chunks_jsonl` — Persistence
- [x] CLI test script (`cli_ingest.py`)
- [x] `requirements.txt`

### Test It
```bash
cd /Users/aliasgarmomin/codepilot
pip install -r requirements.txt
python api/cli_ingest.py data/fastapi/fastapi
```

---

## 🔨 Phase 2: Embeddings & Vector Index (NEXT)

### 2.1 Embeddings Module (`api/embeddings.py`)
**Status:** Not started  
**Estimated time:** 1-2 hours

**Components needed:**
- [ ] `load_embedding_model()` — Load SentenceTransformer (e.g., `all-MiniLM-L6-v2`)
- [ ] `embed_texts(texts: list[str]) -> np.ndarray` — Batch encode + L2 normalize
- [ ] `embed_single(text: str) -> np.ndarray` — Single query encoding
- [ ] Caching logic (optional, for repeat queries)

**Key decisions:**
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384 dims, 80MB, fast)
- Normalization: L2 norm for cosine similarity
- Batch size: 32-64 for encoding

**Test it:**
```python
from embeddings import load_embedding_model, embed_texts

model = load_embedding_model()
vecs = embed_texts(["def authenticate(token)", "function login()"])
print(vecs.shape)  # Should be (2, 384)
print(np.linalg.norm(vecs[0]))  # Should be ~1.0 (normalized)
```

---

### 2.2 FAISS Index Module (`api/vector_index.py`)
**Status:** Not started  
**Estimated time:** 1-2 hours

**Components needed:**
- [ ] `build_index(embeddings: np.ndarray) -> faiss.Index` — Create IndexFlatIP (inner product)
- [ ] `save_index(index, path: Path)` — Persist to disk
- [ ] `load_index(path: Path) -> faiss.Index` — Load from disk
- [ ] `search_index(index, query_vec, k, oversample_factor)` — Top-k retrieval

**Key decisions:**
- Index type: `IndexFlatIP` (exact search, works with normalized vectors)
- Oversample: Retrieve `k * oversample_factor` results before filtering

**Test it:**
```python
from vector_index import build_index, search_index
import numpy as np

# Dummy data
embeddings = np.random.randn(100, 384).astype('float32')
embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)

index = build_index(embeddings)
query = np.random.randn(384).astype('float32')
query /= np.linalg.norm(query)

distances, indices = search_index(index, query, k=5, oversample_factor=2)
print(indices)  # Should return [10 relevant chunk IDs]
```

---

## 🌐 Phase 3: Search API (FastAPI)

### 3.1 API Server (`api/main.py`)
**Status:** Not started  
**Estimated time:** 2-3 hours

**Endpoints needed:**
- [ ] `POST /ingest` — Trigger repo ingestion
  - Input: `{ repo_path, include_exts?, exclude_dirs?, window?, overlap? }`
  - Output: `{ files_scanned, files_read, chunks_total, avg_lines_per_chunk }`
  - Side effects: Saves JSONL + builds FAISS index

- [ ] `GET /status` — Check if system is ready
  - Output: `{ indexed: bool, chunks: int, last_ingest: timestamp? }`

- [ ] `GET /search` — Semantic search
  - Query params: `q` (string), `k` (int, default 5), `pathContains?`, `lang?`
  - Output: 
    ```json
    {
      "q": "JWT validation",
      "k": 5,
      "latency_ms": 87,
      "results": [
        {
          "repo": "fastapi",
          "path": "fastapi/security/oauth2.py",
          "start_line": 42,
          "end_line": 73,
          "preview": "...",
          "score": 0.87,
          "lang": "python"
        }
      ]
    }
    ```

- [ ] `GET /health` — Basic health check

**Key features:**
- Load model & index on startup (singleton pattern)
- Error handling for missing index
- CORS middleware for frontend
- Request timing middleware

**Project structure:**
```
api/
├── main.py              # FastAPI app
├── ingest.py            # ✅ Done
├── embeddings.py        # To do
├── vector_index.py      # To do
├── search.py            # Search logic (filter/rerank)
├── cli_ingest.py        # ✅ Done
└── config.py            # Paths & constants (optional)
```

---

### 3.2 Search Logic (`api/search.py`)
**Status:** Not started  
**Estimated time:** 1 hour

**Components needed:**
- [ ] `filter_results(chunks, indices, scores, path_filter?, lang_filter?)` — Post-retrieval filtering
- [ ] `keyword_boost(chunks, indices, scores, query)` — Optional: bump exact keyword matches
- [ ] `assemble_results(chunks, indices, scores, k)` — Format final output

**Logic flow:**
1. Embed query
2. Oversample from FAISS (e.g., 5× k)
3. Apply filters (path substring, language)
4. (Optional) Keyword micro-rerank
5. Truncate to k
6. Assemble JSON response

---

## 🎨 Phase 4: Frontend (Next.js)

### 4.1 Project Setup
**Status:** Not started  
**Estimated time:** 30 min

```bash
cd web
npx create-next-app@latest . --typescript --tailwind --app
```

**Key pages:**
- `/` — Search page (main UI)
- (Optional) `/ingest` — Admin page to trigger ingestion

---

### 4.2 Search Page (`web/app/page.tsx`)
**Status:** Not started  
**Estimated time:** 2-3 hours

**Components needed:**
- [ ] Search input (with debounce)
- [ ] Filters: repo selector, path substring, language dropdown
- [ ] Results list:
  - File path (clickable)
  - Line range badge
  - Preview snippet (syntax highlighting optional)
  - Similarity score
  - "Copy link" / "Open in GitHub" buttons
- [ ] Loading spinner
- [ ] Empty state / error handling

**UI polish:**
- Tailwind for styling
- Syntax highlighting: `react-syntax-highlighter` or `prism-react-renderer`
- Icons: `lucide-react` or `heroicons`

---

### 4.3 API Client (`web/lib/api.ts`)
**Status:** Not started  
**Estimated time:** 30 min

```typescript
export async function searchCode(query: string, k: number = 5, filters?: {
  pathContains?: string;
  lang?: string;
}) {
  const params = new URLSearchParams({ q: query, k: k.toString() });
  if (filters?.pathContains) params.set('pathContains', filters.pathContains);
  if (filters?.lang) params.set('lang', filters.lang);
  
  const res = await fetch(`http://localhost:8000/search?${params}`);
  return res.json();
}

export async function getStatus() {
  const res = await fetch('http://localhost:8000/status');
  return res.json();
}
```

---

## 📊 Phase 5: Evaluation & Metrics

### 5.1 Golden Test Set (`evaluation/goldens.json`)
**Status:** Not started  
**Estimated time:** 1 hour

**Task:** Create 20-30 test queries for the FastAPI repo with expected files.

Example:
```json
[
  {
    "query": "How do I validate JWT tokens?",
    "expected_files": ["fastapi/security/oauth2.py", "fastapi/security/http.py"]
  },
  {
    "query": "Where are dependency injection resolvers?",
    "expected_files": ["fastapi/dependencies/utils.py"]
  }
]
```

---

### 5.2 Evaluation Script (`evaluation/eval.py`)
**Status:** Not started  
**Estimated time:** 1-2 hours

**Components needed:**
- [ ] Load goldens
- [ ] Run searches
- [ ] Calculate precision@5, precision@10
- [ ] Measure latency (p50, p95, p99)
- [ ] Generate report

**Output:**
```
=== CodePilot Evaluation ===
Queries:     30
Precision@5: 86.7%
Precision@10: 93.3%

Latency (ms):
  p50:  127
  p95:  243
  p99:  312

Index size: 10,247 chunks
```

---

### 5.3 Integrate Metrics into API
**Status:** Not started  
**Estimated time:** 30 min

**Add to `/status` endpoint:**
```json
{
  "indexed": true,
  "chunks": 10247,
  "last_ingest": "2025-10-16T10:23:00Z",
  "metrics": {
    "precision_at_5": 0.867,
    "avg_latency_ms": 127,
    "p95_latency_ms": 243
  }
}
```

---

## 🚀 Phase 6: Polish & Deployment

### 6.1 Docker Setup
**Status:** Not started  
**Estimated time:** 1 hour

**Files needed:**
- [ ] `Dockerfile` (API)
- [ ] `web/Dockerfile` (Frontend)
- [ ] `docker-compose.yml` (orchestrate both)

**Example `docker-compose.yml`:**
```yaml
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - MODEL_CACHE_DIR=/app/.cache

  web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - api
```

---

### 6.2 README Polish
**Status:** Not started  
**Estimated time:** 1 hour

**Sections to add:**
- [ ] Architecture diagram
- [ ] Demo GIF / screenshots
- [ ] Quick start instructions
- [ ] Performance metrics table
- [ ] Design decisions explanation
- [ ] Future work / roadmap

---

### 6.3 Optional Enhancements (Post-MVP)
**Status:** Not started

**Ideas:**
- [ ] Hybrid search (BM25 + vector fusion)
- [ ] Query caching (LRU cache for embeddings)
- [ ] Incremental indexing (watch mode)
- [ ] Multi-repo support
- [ ] AST-based chunking (tree-sitter)
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Export results to CSV/JSON

---

## 📅 Estimated Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| ✅ Phase 1: Ingestion | 8 components | **~4 hours** (DONE) |
| 🔨 Phase 2: Embeddings & Index | 2 modules | **~3 hours** |
| 🌐 Phase 3: Search API | 3 modules | **~4 hours** |
| 🎨 Phase 4: Frontend | UI + client | **~3 hours** |
| 📊 Phase 5: Evaluation | Goldens + metrics | **~3 hours** |
| 🚀 Phase 6: Polish | Docker + README | **~2 hours** |
| **TOTAL** | | **~19 hours** |

**Realistic timeline:** 1 week working 3-4 hours/day

---

## 🎯 Success Criteria (MVP Complete)

- [x] Can ingest a repo and create chunks ✅
- [ ] Can build FAISS index from embeddings
- [ ] API returns search results in < 200ms (p50)
- [ ] Precision@5 ≥ 80% on golden set
- [ ] Clean web UI with search + filters
- [ ] README with metrics & screenshots
- [ ] Docker setup works out of the box

---

## 📝 Notes

**Current progress:** Phase 1 complete (ingestion pipeline fully functional)

**Next immediate steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Test ingestion: `python api/cli_ingest.py data/fastapi/fastapi`
3. Verify output: check `output/chunks.jsonl`
4. Move to Phase 2: embeddings module

**Test data:** Using FastAPI repo (already in `data/fastapi/`) — perfect Python-heavy codebase for testing.

