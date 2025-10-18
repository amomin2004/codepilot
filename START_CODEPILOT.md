# 🚀 How to Start CodePilot

Quick reference for starting CodePilot after shutdown.

---

## ⚡ **Quick Start (2 Terminals)**

### **Terminal 1: Start Backend**
```bash
cd /Users/aliasgarmomin/codepilot
python3 api/main.py
```

Wait for: `🚀 CodePilot API ready!`

### **Terminal 2: Start Frontend**
```bash
cd /Users/aliasgarmomin/codepilot/web
npm run dev
```

Wait for: `Ready on http://localhost:3000`

---

## 🌐 **Access the Application**

- **Web Interface:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## 🐳 **Alternative: Docker**

```bash
cd /Users/aliasgarmomin/codepilot
docker-compose up -d
```

Stop:
```bash
docker-compose down
```

---

## ✅ **Verify Everything Works**

### **1. Check API:**
```bash
curl http://localhost:8000/health
```

### **2. Check Frontend:**
```bash
curl http://localhost:3000
```

### **3. Test Search:**
1. Go to http://localhost:3000
2. Try a search query
3. Verify results appear

---

## 🛑 **Stop Everything**

```bash
# Kill all processes
ps aux | grep -E "(api/main.py|npm run dev)" | grep -v grep | awk '{print $2}' | xargs kill -9

# Or manually:
# Ctrl+C in both terminals
```

---

## 📋 **Before Deploying**

- [ ] Test locally works (both terminals running)
- [ ] Search returns results
- [ ] GitHub URL ingestion works
- [ ] No errors in terminal
- [ ] Commit all changes
- [ ] Push to GitHub
- [ ] Follow DEPLOYMENT.md

---

**See you tomorrow! 👋**

