# CodePilot — TODO Checklist

## ✅ COMPLETED (Phase 1)

- [x] Project structure setup
- [x] Requirements file with dependencies
- [x] File discovery (`list_source_files`)
- [x] Safe file reading with encoding detection (`read_text_safely`)
- [x] Fixed-window chunking with overlap (`chunk_lines`)
- [x] Language detection (`detect_lang_from_ext`)
- [x] Content hashing for deduplication (`hash_text`)
- [x] Preview generation (`make_preview`)
- [x] Main ingestion orchestrator (`ingest_repo`)
- [x] JSONL persistence (`save_chunks_jsonl`, `load_chunks_jsonl`)
- [x] CLI testing tool (`cli_ingest.py`)
- [x] Unit tests (8 tests, all passing)
- [x] Documentation (ROADMAP.md, PROGRESS.md)
- [x] .gitignore

---

## 🔨 PHASE 2: Embeddings & Vector Index

### Module: `api/embeddings.py`
- [ ] Load SentenceTransformer model (`all-MiniLM-L6-v2`)
- [ ] Batch encode chunks (`embed_texts()`)
- [ ] L2 normalize vectors for cosine similarity
- [ ] Single query encoding (`embed_single()`)
- [ ] Add simple caching (optional)
- [ ] Write unit tests

### Module: `api/vector_index.py`
- [ ] Build FAISS IndexFlatIP (`build_index()`)
- [ ] Save index to disk (`save_index()`)
- [ ] Load index from disk (`load_index()`)
- [ ] Search with oversampling (`search_index()`)
- [ ] Handle edge cases (empty index, invalid k)
- [ ] Write unit tests

### Integration Test
- [ ] End-to-end test: ingest → embed → index → search
- [ ] Verify cosine similarity scores
- [ ] Check index-to-metadata alignment

**Estimated time:** 3 hours

---

## 🌐 PHASE 3: Search API

### Module: `api/search.py`
- [ ] Filter results by path substring (`filter_by_path()`)
- [ ] Filter results by language (`filter_by_lang()`)
- [ ] Optional keyword boost (`keyword_boost()`)
- [ ] Assemble final results (`assemble_results()`)
- [ ] Add latency tracking

### Module: `api/config.py` (optional)
- [ ] Centralize paths (JSONL, FAISS index)
- [ ] Default parameters (k, window, overlap)
- [ ] Model configuration

### Module: `api/main.py` (FastAPI)
- [ ] Initialize FastAPI app
- [ ] Load model & index on startup
- [ ] `POST /ingest` endpoint
  - [ ] Input validation (Pydantic models)
  - [ ] Call `ingest_repo()`
  - [ ] Build embeddings
  - [ ] Build & save FAISS index
  - [ ] Return stats
- [ ] `GET /status` endpoint
  - [ ] Check if index exists
  - [ ] Return chunk count, timestamp
  - [ ] (Later) Add metrics
- [ ] `GET /search` endpoint
  - [ ] Query param validation
  - [ ] Embed query
  - [ ] Search FAISS
  - [ ] Apply filters
  - [ ] Return formatted results
  - [ ] Track latency
- [ ] `GET /health` endpoint
- [ ] Add CORS middleware
- [ ] Add timing middleware
- [ ] Error handling (404, 500, validation errors)

### Testing
- [ ] Test each endpoint with `curl` or Postman
- [ ] Verify response format
- [ ] Check error handling
- [ ] Measure latency

**Estimated time:** 4 hours

---

## 🎨 PHASE 4: Frontend (Next.js)

### Setup
- [ ] Create Next.js app in `web/`
- [ ] Configure TypeScript + Tailwind
- [ ] Install UI dependencies (`lucide-react`, `react-syntax-highlighter`)

### API Client (`web/lib/api.ts`)
- [ ] `searchCode()` function
- [ ] `getStatus()` function
- [ ] `triggerIngest()` function (optional)
- [ ] Error handling

### Main Page (`web/app/page.tsx`)
- [ ] Search input with debounce
- [ ] Filter controls:
  - [ ] Path substring filter
  - [ ] Language dropdown
  - [ ] Results count (k) slider
- [ ] Results display:
  - [ ] File path (clickable)
  - [ ] Line range badge
  - [ ] Preview snippet
  - [ ] Similarity score
  - [ ] Language badge
  - [ ] "Copy" button
  - [ ] "Open in GitHub" button (if GitHub repo)
- [ ] Loading state
- [ ] Empty state ("No results")
- [ ] Error handling

### Styling
- [ ] Responsive layout
- [ ] Syntax highlighting for previews
- [ ] Nice typography
- [ ] Loading spinner
- [ ] Hover effects

**Estimated time:** 3 hours

---

## 📊 PHASE 5: Evaluation & Metrics

### Golden Test Set (`evaluation/goldens.json`)
- [ ] Create 20-30 test queries for FastAPI repo
- [ ] List expected files for each query
- [ ] Cover diverse query types:
  - [ ] Security ("JWT validation")
  - [ ] Config ("environment variables")
  - [ ] Features ("WebSocket handling")
  - [ ] Error handling
  - [ ] Middleware

### Evaluation Script (`evaluation/eval.py`)
- [ ] Load golden queries
- [ ] Run searches via API
- [ ] Calculate precision@5 and precision@10
- [ ] Measure latency (p50, p95, p99)
- [ ] Generate report
- [ ] Save results to JSON

### Integrate into API
- [ ] Add `/metrics` endpoint (or extend `/status`)
- [ ] Expose precision@k
- [ ] Expose latency stats
- [ ] Last evaluation timestamp

**Estimated time:** 3 hours

---

## 🚀 PHASE 6: Polish & Deployment

### Docker Setup
- [ ] Create `api/Dockerfile`
- [ ] Create `web/Dockerfile`
- [ ] Create `docker-compose.yml`
- [ ] Test full stack with Docker
- [ ] Add health checks

### Documentation
- [ ] Update README with:
  - [ ] Architecture diagram
  - [ ] Demo GIF or screenshots
  - [ ] Quick start guide
  - [ ] Performance metrics table
  - [ ] Design decisions
  - [ ] API documentation
  - [ ] Troubleshooting
- [ ] Add inline code comments
- [ ] Create CONTRIBUTING.md (optional)

### Final Testing
- [ ] Fresh install test (new machine simulation)
- [ ] Cross-platform test (if possible)
- [ ] Load test (large repo)
- [ ] Edge cases (empty repo, weird encodings)

### Optional Enhancements
- [ ] Query caching (LRU)
- [ ] Hybrid search (BM25 + vector)
- [ ] Dark mode toggle
- [ ] Keyboard shortcuts
- [ ] Export results to CSV

**Estimated time:** 2 hours

---

## 🎯 MVP COMPLETE CRITERIA

- [x] ✅ Ingestion pipeline functional
- [ ] Can build FAISS index
- [ ] API returns search results
- [ ] Web UI displays results
- [ ] Latency < 200ms (p50)
- [ ] Precision@5 ≥ 80%
- [ ] Docker setup works
- [ ] README with metrics & screenshots

---

## 📅 Time Estimates Summary

| Phase | Status | Time |
|-------|--------|------|
| Phase 1: Ingestion | ✅ Done | ~2h |
| Phase 2: Embeddings + Index | 🔨 Next | ~3h |
| Phase 3: Search API | ⏳ | ~4h |
| Phase 4: Frontend | ⏳ | ~3h |
| Phase 5: Evaluation | ⏳ | ~3h |
| Phase 6: Polish | ⏳ | ~2h |
| **TOTAL** | | **~17h** |

**Current progress:** ~12% (Phase 1 complete)  
**Next milestone:** Working search API (Phases 2-3)  
**Time to first search:** ~7 more hours  
**Time to MVP:** ~15 more hours

---

## 🎬 Next Actions (In Order)

1. **Install remaining dependencies:**
   ```bash
   pip install sentence-transformers faiss-cpu torch numpy
   ```

2. **Create `api/embeddings.py`:**
   - Start with model loading
   - Add batch encoding
   - Test with sample text

3. **Create `api/vector_index.py`:**
   - Build FAISS index
   - Test save/load
   - Test search

4. **Integration test:**
   - Ingest → embed → index → search
   - Verify everything connects

5. **Build FastAPI server:**
   - Start with `/health` and `/status`
   - Add `/ingest`
   - Add `/search`
   - Test with curl

6. **Move to frontend:**
   - Only after API is solid

---

## 💡 Pro Tips

- **Test incrementally:** Don't build everything before testing
- **Use real data:** Test on the FastAPI repo early
- **Measure everything:** Track latency from day 1
- **Keep it simple:** MVP first, enhancements later
- **Document as you go:** Update README with each milestone

---

## 🏁 When You're Done

You'll have:
- A production-quality semantic code search engine
- Measurable performance metrics
- A polished demo
- Portfolio-ready documentation
- Interview talking points about design decisions

Let's build! 🚀

