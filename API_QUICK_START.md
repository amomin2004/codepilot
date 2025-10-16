# CodePilot API - Quick Start Guide

## 🚀 Start the Server

```bash
cd /Users/aliasgarmomin/codepilot
python api/main.py
```

Server will start on: **http://localhost:8000**

---

## 📖 API Documentation

Visit these URLs while the server is running:

- **Interactive API docs:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health
- **System status:** http://localhost:8000/status

---

## 🔥 Quick Test

### 1. Check if server is running:
```bash
curl http://localhost:8000/health
```

### 2. Ingest a repository:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "data/fastapi/fastapi",
    "window": 80,
    "overlap": 15
  }'
```

**Wait 5-10 seconds for ingestion to complete.**

### 3. Search the code:
```bash
# Basic search
curl "http://localhost:8000/search?q=JWT%20validation&k=5"

# Search with language filter
curl "http://localhost:8000/search?q=dependency%20injection&lang=python&k=5"

# Search with path filter
curl "http://localhost:8000/search?q=middleware&path_contains=routing&k=5"
```

---

## 🎯 Example Queries

Try these on the FastAPI repo:

```bash
# Authentication
curl "http://localhost:8000/search?q=How%20to%20validate%20JWT%20tokens"

# WebSockets
curl "http://localhost:8000/search?q=WebSocket%20connection%20handling"

# Dependency Injection
curl "http://localhost:8000/search?q=dependency%20injection&lang=python"

# Middleware
curl "http://localhost:8000/search?q=middleware%20configuration"

# Error Handling
curl "http://localhost:8000/search?q=exception%20handlers"
```

---

## 🧪 Run Tests

### Unit tests:
```bash
python api/test_phase3.py
```

### Integration tests (requires server running):
```bash
# Terminal 1: Start server
python api/main.py

# Terminal 2: Run tests
python api/test_server.py
```

---

## 📊 Expected Performance

| Operation | Time |
|-----------|------|
| Server startup | 1-2s |
| Model loading | 1-2s (on startup) |
| Ingestion (50 files) | 5-10s |
| First search query | 100-200ms |
| Subsequent queries | 20-100ms |

---

## 🛠️ Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill any process using it
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```

### Model download fails?
The embedding model (~80MB) downloads on first use. If it fails:
```bash
# Try manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### No results from search?
Make sure you've run ingestion first:
```bash
curl http://localhost:8000/status
# Should show: "indexed": true
```

---

## 🔑 Environment Variables (Optional)

```bash
# Model cache directory
export HF_HOME="/path/to/cache"

# Log level
export LOG_LEVEL="DEBUG"
```

---

## 📝 Response Examples

### `/status` Response:
```json
{
  "indexed": true,
  "chunks": 308,
  "last_ingest": "2025-10-16T18:15:54.430832",
  "model_loaded": true,
  "index_loaded": true
}
```

### `/search` Response:
```json
{
  "query": "JWT validation",
  "k": 5,
  "total_results": 5,
  "latency_ms": 173.94,
  "results": [
    {
      "repo": "fastapi",
      "path": "security/http.py",
      "lang": "python",
      "start_line": 261,
      "end_line": 340,
      "preview": "class HTTPBearer(HTTPBase):\n    def __init__(...",
      "score": 0.271
    }
  ]
}
```

---

## 🎉 You're Ready!

The API is fully functional. Try different queries and see how semantic search works!

**Next:** Build the web UI (Phase 4) for a better user experience. 🎨

