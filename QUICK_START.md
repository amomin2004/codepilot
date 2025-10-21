# CodePilot Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites Check

Make sure you have these installed:
```bash
python3 --version  # Need 3.11+
node --version     # Need 18+
npm --version
git --version
```

If missing, download from:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Git: https://git-scm.com/downloads

### 2. Download CodePilot

```bash
git clone https://github.com/amomin2004/codepilot.git
cd codepilot
```

### 3. Install Dependencies

```bash
# Backend
pip3 install -r requirements.txt

# Frontend
cd web
npm install
cd ..
```

### 4. Configure Frontend

Create `web/.env.local`:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > web/.env.local
```

### 5. Start Services

**Terminal 1 - Backend:**
```bash
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

### 6. Open Application

Browser: http://localhost:3000

---

## 📚 First Search Example

### Step 1: Index a Repository

1. Go to http://localhost:3000/ingest
2. Enter: `https://github.com/tiangolo/fastapi`
3. Click "Start Indexing" (wait ~60 seconds)

### Step 2: Search

1. Go to http://localhost:3000
2. Type: `How do I validate JWT tokens?`
3. Press Enter

You should see relevant code examples from FastAPI!

---

## 🎯 Try These Queries

After indexing FastAPI:
- "How do I validate JWT tokens?"
- "Where is OAuth2 implemented?"
- "How do I secure API endpoints?"
- "Show me authentication middleware"

---

## 🔧 Quick Troubleshooting

**Backend not starting?**
- Make sure you're in the project root directory
- Use `python3 -m uvicorn api.main:app ...` not just `python`

**Frontend can't connect?**
- Check `web/.env.local` exists
- Restart frontend after creating `.env.local`

**Port already in use?**
```bash
# macOS/Linux - Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 📖 Full Documentation

See [README.md](README.md) for:
- Detailed setup instructions
- API documentation
- Advanced features
- Deployment guides
- Performance metrics

## 🆘 Need Help?

- API Docs: http://localhost:8000/docs
- System Status: http://localhost:8000/status
- GitHub Issues: https://github.com/amomin2004/codepilot/issues

