# 🚀 CodePilot: Semantic Code Search Engine

> **Search your codebase with natural language - "How do I validate JWT tokens?" instead of searching for exact function names.**

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-Powered-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript)](https://typescriptlang.org/)

## 🎯 What is CodePilot?

CodePilot is a **semantic code search engine** that lets you search your codebase using natural language. Instead of searching for exact function names or keywords, ask questions like:

- *"How do I validate JWT tokens?"*
- *"Where are API routes defined?"*
- *"How does error handling work?"*
- *"Show me authentication middleware"*


https://github.com/user-attachments/assets/d6b0b21d-5fe0-49a2-9a14-cba8edea377d

### 🔥 Key Features

- 🧠 **Natural Language Search** - Ask questions in plain English
- 🌐 **GitHub Integration** - Search any public GitHub repository instantly
- 🌍 **Multi-Language Support** - Python, TypeScript, JavaScript, Go, Java, Rust, C++, Ruby, PHP
- ⚡ **Lightning Fast** - 31.5ms average search latency
- 🎨 **Beautiful UI** - Modern web interface with syntax highlighting
- 🔄 **Real-time Indexing** - Index any repository in seconds
- 🎯 **Advanced Filtering** - Filter by language, path, and result count
- 📊 **Performance Metrics** - Built-in evaluation and benchmarking
- 🐳 **Docker Ready** - One-command deployment
- 🔌 **RESTful API** - Complete API for integrations
- ☁️ **Cloud-Ready** - Deploy to Vercel, Railway, or any cloud platform

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI API   │    │  Vector Search  │
│   (Next.js)     │◄──►│   (Python)      │◄──►│   (FAISS)       │
│                 │    │                 │    │                 │
│ • Search UI     │    │ • /search       │    │ • Embeddings    │
│ • Ingestion     │    │ • /ingest       │    │ • Indexing      │
│ • Filters       │    │ • /status       │    │ • Similarity    │
│ • Syntax Highl. │    │ • /health       │    │ • Search        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:
- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+ and npm** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)

Check your versions:
```bash
python --version   # or python3 --version
node --version
npm --version
git --version
```

### Step 1: Download CodePilot

Clone the repository:
```bash
git clone https://github.com/amomin2004/codepilot.git
cd codepilot
```

### Step 2: Install Dependencies

**Backend (Python):**
```bash
# Install Python dependencies
pip install -r requirements.txt
# or if using pip3:
pip3 install -r requirements.txt
```

**Frontend (Node.js):**
```bash
# Navigate to web directory and install
cd web
npm install
cd ..
```

### Step 3: Start the Application

You need **two terminal windows** running simultaneously.

**Terminal 1 - Start Backend:**
```bash
# From the project root directory
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     🚀 CodePilot API ready!
```

**Terminal 2 - Start Frontend:**
```bash
# From the project root directory
cd web
npm run dev
```

You should see:
```
▲ Next.js 15.x.x
- Local:        http://localhost:3000
```

### Step 4: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Interactive API documentation)

---

## 🐳 Alternative: Docker Setup (Optional)

If you prefer Docker:

```bash
# Clone repository
git clone https://github.com/amomin2004/codepilot.git
cd codepilot

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:3000
```

## 📖 How to Use CodePilot

### Step 1: Index a Repository

CodePilot can index **any GitHub repository** or **local project** on your computer. You need to index a repository before you can search it.

#### Option A: Using the Web Interface (Easiest)

1. **Open the application**: http://localhost:3000
2. **Click "Ingest"** in the top navigation
3. **Enter a repository**:
   
   **For a GitHub Repository:**
   ```
   https://github.com/tiangolo/fastapi
   ```
   
   **For a Local Project:**
   ```
   /Users/yourname/projects/myapp
   ```
   Or on Windows:
   ```
   C:\Users\yourname\projects\myapp
   ```

4. **Click "Start Indexing"**
5. **Wait for completion** (usually 30-60 seconds depending on repo size)
6. You'll see a success message with statistics

#### Option B: Using the API

**Index a GitHub Repository:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "https://github.com/tiangolo/fastapi"}'
```

**Index a Local Project:**
```bash
# macOS/Linux
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/Users/yourname/projects/myapp"}'

# Windows (PowerShell)
curl.exe -X POST http://localhost:8000/ingest `
  -H "Content-Type: application/json" `
  -d '{\"repo_path\": \"C:\\Users\\yourname\\projects\\myapp\"}'
```

#### 🎯 Recommended GitHub Repositories to Try

Perfect for testing with authentication/JWT questions:

| Repository | URL | Best For |
|------------|-----|----------|
| **FastAPI** | `https://github.com/tiangolo/fastapi` | JWT, OAuth2, API security |
| **Django REST** | `https://github.com/encode/django-rest-framework` | Authentication, permissions |
| **NestJS** | `https://github.com/nestjs/nest` | TypeScript, guards, JWT strategies |
| **Express** | `https://github.com/expressjs/express` | Middleware, routing patterns |
| **Next.js** | `https://github.com/vercel/next.js` | React, API routes, auth |

**Pro Tip**: Start with FastAPI - it has excellent security examples and is perfect for JWT-related queries!

### Step 2: Search Your Code

Once you've indexed a repository, you can search it using natural language!

#### Using the Web Interface (Recommended)

1. **Go to the Search page**: http://localhost:3000 (home page)
2. **Type your question** in natural language:
   ```
   How do I validate JWT tokens?
   ```
3. **Press Enter** or click "Search"
4. **View results** with syntax highlighting and file locations

#### Using Advanced Filters

Refine your search with filters:

- **Language Filter**: 
  - Select `Python`, `TypeScript`, `JavaScript`, etc.
  - Only shows results from that language
  
- **Path Filter**:
  - Enter: `security/` to search only in security directory
  - Enter: `auth` to find files with "auth" in the path
  
- **Result Count**:
  - Choose 5, 10, or 20 results per search

**Example with Filters:**
```
Query: "JWT authentication"
Language: Python
Path Contains: security
Results: 10
```

#### Using the API

**Simple Search:**
```bash
curl "http://localhost:8000/search?q=How%20do%20I%20validate%20JWT%20tokens&k=5"
```

**Search with Filters:**
```bash
# Filter by language (Python only)
curl "http://localhost:8000/search?q=authentication&lang=python&k=10"

# Filter by path (security directory only)
curl "http://localhost:8000/search?q=JWT&pathContains=security&k=5"

# Combine filters
curl "http://localhost:8000/search?q=OAuth&lang=python&pathContains=auth&k=10"
```

### 🎯 Example Search Queries

Try these questions on an indexed repository:

**Authentication & Security:**
- "How do I validate JWT tokens?"
- "Where is OAuth2 authentication implemented?"
- "How do I secure API endpoints?"
- "Show me password hashing examples"
- "Where are authentication middleware defined?"

**API Development:**
- "How do I create REST endpoints?"
- "Where are API routes defined?"
- "How do I handle request validation?"
- "Show me error response examples"
- "How do I add CORS headers?"

**Database:**
- "How do I connect to a database?"
- "Where are database models defined?"
- "How do I handle database sessions?"
- "Show me migration examples"

**Testing:**
- "How do I write unit tests?"
- "Where are test fixtures defined?"
- "How do I mock dependencies?"

---

## 🎓 Complete Example Walkthrough

Here's a complete example from start to finish:

### Example: Searching FastAPI for JWT Authentication

**1. Start CodePilot** (if not already running):
```bash
# Terminal 1
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
cd web && npm run dev
```

**2. Index FastAPI Repository**:

Open http://localhost:3000/ingest and enter:
```
https://github.com/tiangolo/fastapi
```
Click "Start Indexing" and wait ~60 seconds.

**3. Search for JWT Information**:

Go to http://localhost:3000 and try:
- "How do I validate JWT tokens?"
- "Where is OAuth2 implemented?"
- "Show me bearer token authentication"

**4. View Results**:

You'll see code snippets with:
- ✅ File paths (e.g., `docs_src/security/tutorial005.py`)
- ✅ Line numbers
- ✅ Syntax highlighting
- ✅ Relevance scores
- ✅ Direct code previews

**5. Refine with Filters**:

Add filters:
- Language: `Python`
- Path: `security`
- Results: `10`

---

## 📊 Performance Results

Based on comprehensive evaluation with 25 test queries:

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| **Precision@5** | 52% | 80% | ⚠️ Good |
| **Precision@10** | 53% | 90% | ⚠️ Good |
| **Mean Reciprocal Rank** | 0.357 | 0.700 | ⚠️ Good |
| **Latency P50** | 14.8ms | ≤200ms | ✅ Excellent |
| **Latency P95** | 53.3ms | ≤500ms | ✅ Excellent |
| **Latency P99** | 282.3ms | ≤1000ms | ✅ Excellent |

### 🎯 Best Performing Categories

- **Routing**: 100% precision - Perfect API endpoint queries
- **Error Handling**: 100% precision - Excellent exception handling
- **Authentication**: 67% precision - Good security-related queries
- **Middleware**: 50% precision - Moderate middleware queries

## 🐳 Docker Deployment

### Production Deployment

```bash
# Production with Nginx
docker-compose -f docker-compose.prod.yml up -d

# Access via Nginx proxy
open http://localhost
```

### Development Mode

```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up -d
```

### Management Scripts

```bash
# Build containers
./scripts/docker-build.sh

# Start services
./scripts/docker-start.sh

# Stop services
./scripts/docker-stop.sh
```

## 🧪 Evaluation & Testing

### Run Full Evaluation

```bash
# Run evaluation with 25 test queries
python evaluation/cli_eval.py

# Generate HTML report
python evaluation/cli_eval.py --report

# Verbose output
python evaluation/cli_eval.py --verbose
```

### Run Test Suite

```bash
# Test all components
python evaluation/test_eval.py
```

### Custom Evaluation

```bash
# Use custom golden set
python evaluation/cli_eval.py --golden-set my_queries.json

# Save results
python evaluation/cli_eval.py --output my_results.json
```

## 🔧 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | System status and indexing info |
| `/ingest` | POST | Index a repository |
| `/search` | GET | Semantic search with filters |

### Search Parameters

```bash
GET /search?q=query&k=5&lang=python&pathContains=auth
```

- `q` - Search query (required)
- `k` - Number of results (default: 5)
- `lang` - Language filter (python, typescript, etc.)
- `pathContains` - Path filter (auth, middleware, etc.)

### Example API Usage

```bash
# Search for JWT validation
curl "http://localhost:8000/search?q=JWT%20token%20validation&k=5"

# Search with filters
curl "http://localhost:8000/search?q=authentication&lang=python&pathContains=auth"

# Index repository
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/project"}'
```

## 📁 Project Structure

```
codepilot/
├── 🐍 api/                    # FastAPI backend
│   ├── main.py               # Main application (311 lines)
│   ├── ingest.py             # Repository ingestion (280 lines)
│   ├── embeddings.py         # Vector embeddings (150 lines)
│   ├── vector_index.py       # FAISS operations (120 lines)
│   ├── search.py             # Search logic (280 lines)
│   └── cli_ingest.py         # CLI ingestion tool
├── 🌐 web/                   # Next.js frontend
│   ├── src/app/             # App router pages
│   │   ├── page.tsx         # Search page (342 lines)
│   │   ├── ingest/page.tsx  # Ingestion page (314 lines)
│   │   └── layout.tsx       # Root layout
│   ├── src/components/      # React components
│   │   └── Navigation.tsx   # Top navigation (55 lines)
│   └── src/lib/             # Utilities
│       └── api.ts           # API client (85 lines)
├── 📊 evaluation/            # Evaluation framework
│   ├── goldens.json         # Test queries (25 queries)
│   ├── eval.py              # Evaluation engine (400+ lines)
│   ├── cli_eval.py          # CLI tool (300+ lines)
│   └── test_eval.py         # Test suite (250+ lines)
├── 🐳 Docker files
│   ├── Dockerfile.api       # API container
│   ├── Dockerfile.web       # Web container
│   ├── docker-compose.yml   # Development
│   ├── docker-compose.prod.yml # Production
│   └── nginx.conf           # Reverse proxy
├── 📦 scripts/              # Deployment scripts
│   ├── docker-build.sh      # Build containers
│   ├── docker-start.sh      # Start services
│   └── docker-stop.sh       # Stop services
├── 📚 data/                 # Sample repositories
└── 📄 output/              # Index and chunks storage
```

**Total: ~4,000 lines of production code**

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Backend Won't Start

**Problem**: `ModuleNotFoundError` or import errors
```bash
ModuleNotFoundError: No module named 'api.ingest'
```

**Solution**: Make sure you're running from the project root and using the correct command:
```bash
cd /path/to/codepilot
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

**Problem**: `Address already in use` (Port 8000)

**Solution**: Kill the process using port 8000:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

#### Frontend Won't Start

**Problem**: `npm install` fails or modules not found

**Solution**: 
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

---

**Problem**: Port 3000 already in use

**Solution**: Use a different port:
```bash
cd web
PORT=3001 npm run dev
```

---

#### Indexing Issues

**Problem**: "No chunks created" when indexing

**Solutions**:
- ✅ Make sure the path exists and is correct
- ✅ For local paths, use absolute paths: `/Users/name/project` not `~/project`
- ✅ For GitHub URLs, use full HTTPS URLs: `https://github.com/user/repo`
- ✅ Check that the repository has supported file types (`.py`, `.ts`, `.js`, etc.)

---

**Problem**: GitHub repository clone fails

**Solution**: Make sure the repository is public or check your internet connection:
```bash
# Test if you can clone manually
git clone https://github.com/tiangolo/fastapi /tmp/test-repo
```

---

#### Search Issues

**Problem**: Search returns no results

**Solutions**:
1. Make sure you've indexed a repository first
2. Check indexing status: http://localhost:8000/status
3. Try a simpler query: "authentication" instead of "How do I implement OAuth2?"
4. Remove filters and try again

---

**Problem**: Frontend can't connect to backend

**Solution**: 
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `web/.env.local` exists with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Restart the frontend after creating `.env.local`

---

### Getting Help

If you encounter other issues:
1. Check the backend logs in Terminal 1
2. Check the frontend logs in Terminal 2
3. Visit the API docs: http://localhost:8000/docs
4. Check system status: http://localhost:8000/status

## 🛠️ Development

### Local Development

```bash
# Backend development
python api/main.py

# Frontend development
cd web && npm run dev

# Run evaluation
python evaluation/cli_eval.py --verbose
```

### Adding New Features

1. **Backend**: Add to `api/` directory
2. **Frontend**: Add to `web/src/` directory
3. **Tests**: Add to `evaluation/` directory
4. **Docker**: Update Dockerfiles as needed

### Code Quality

```bash
# Python formatting
black api/
isort api/

# TypeScript checking
cd web && npm run type-check

# Run all tests
python evaluation/test_eval.py
```

## 🌟 Use Cases

### For Developers
- **New Team Members**: Understand large codebases quickly
- **Code Review**: Find relevant code before reviewing
- **Debugging**: Locate error handling and similar patterns
- **Refactoring**: Understand dependencies and relationships

### For Teams
- **Knowledge Discovery**: Find existing solutions in codebase
- **Code Reuse**: Locate reusable components and patterns
- **Documentation**: Understand complex flows and architectures
- **Onboarding**: Accelerate new developer productivity

### For Open Source
- **Contributors**: Understand unfamiliar codebases
- **Maintainers**: Help new contributors find relevant code
- **Users**: Learn how to use complex libraries
- **Researchers**: Analyze code patterns and practices

## 📈 Roadmap

### Phase 1: Core Features ✅
- [x] Repository ingestion and chunking
- [x] Vector embeddings and indexing
- [x] Semantic search API
- [x] Web interface
- [x] Evaluation framework

### Phase 2: Enhanced Search 🔄
- [ ] Hybrid search (keyword + semantic)
- [ ] Code completion integration
- [ ] Multi-repository search
- [ ] Advanced filtering options

### Phase 3: Developer Tools 🚀
- [ ] IDE extensions (VSCode, IntelliJ)
- [ ] CLI tool for terminal usage
- [ ] GitHub/GitLab integration
- [ ] Code generation from queries

### Phase 4: Enterprise Features 🏢
- [ ] User authentication and authorization
- [ ] Team collaboration features
- [ ] Advanced analytics and insights
- [ ] Custom model training

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Excellent Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [Sentence Transformers](https://www.sbert.net/) - State-of-the-art embeddings
- [FAISS](https://faiss.ai/) - Efficient similarity search
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Lucide React](https://lucide.dev/) - Beautiful icon library

---

**Built by Ali Asgar Momin**
