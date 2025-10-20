# 🚀 Memory Optimization Summary

## Branch: `optimize`

This branch contains memory optimizations to run CodePilot on free-tier hosting services (Render, Railway, etc.) with **<512MB RAM limits**.

---

## 📊 Changes Made

### 1. **Smaller Embedding Model**
- **Before:** `all-MiniLM-L6-v2` (6 transformer layers, ~400MB RAM)
- **After:** `paraphrase-MiniLM-L3-v2` (3 transformer layers, ~200MB RAM)
- **Savings:** ~200MB
- **Accuracy Impact:** ~5-10% reduction (still excellent for code search)

### 2. **CPU-Only PyTorch**
- **Before:** `torch==2.5.0` (includes CUDA libraries, ~350MB)
- **After:** `torch==2.5.0+cpu` (CPU-only, ~150MB)
- **Savings:** ~200MB
- **Performance Impact:** 10-20% slower inference (still fast for demos)

### 3. **Removed Dev Dependencies**
- Removed: `pytest`, `matplotlib`, `seaborn`
- **Savings:** ~100MB
- **Note:** These are still in `main` branch for local development

### 4. **Lazy Model Loading**
- **Before:** Model loads at startup (~20 seconds)
- **After:** Model loads on first request
- **Benefits:**
  - Startup time: 20s → 2s
  - Port opens immediately (prevents Render timeout)
  - First request: ~1.7s (model loads)
  - Subsequent requests: ~280ms (fast!)

---

## 💾 Total Memory Usage

| Component | Main Branch | Optimize Branch | Savings |
|-----------|-------------|-----------------|---------|
| PyTorch | ~350MB | ~150MB | -200MB |
| Embedding Model | ~400MB | ~200MB | -200MB |
| Dev Dependencies | ~100MB | ~0MB | -100MB |
| Base (Python/FastAPI/NumPy/FAISS) | ~130MB | ~130MB | 0 |
| **TOTAL** | **~980MB** | **~480MB** | **-500MB** ✅ |

---

## ✅ Test Results

**Local Testing (optimize branch):**
- ✅ Backend starts in ~2 seconds
- ✅ First search: 1689ms (model loads + search)
- ✅ Subsequent searches: ~284ms (fast!)
- ✅ Memory usage: **<500MB** (fits in 512MB free tier)

---

## 🔄 Branch Strategy

### **`main` branch** (High-Memory, High-Accuracy)
- Use for: Local development, powerful servers
- Memory: ~980MB
- Model: `all-MiniLM-L6-v2` (best accuracy)
- Includes: All dev dependencies

### **`optimize` branch** (Low-Memory, Production)
- Use for: Render, Railway, free-tier deployments
- Memory: ~480MB (fits 512MB limit)
- Model: `paraphrase-MiniLM-L3-v2` (90-95% accuracy)
- Production-only dependencies

---

## 🚀 Deploying to Render

1. **Push optimize branch:**
   ```bash
   git checkout optimize
   git push origin optimize
   ```

2. **In Render Dashboard:**
   - Set Branch: `optimize`
   - Build Command: `pip install -r requirements-render.txt`
   - Start Command: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `PYTHONPATH=/opt/render/project/src`
   
   **Note:** The `requirements-render.txt` file uses CPU-only PyTorch which only works on Linux. For local macOS/Windows development, use `requirements.txt`

3. **Expected behavior:**
   - Build: ~3-5 minutes
   - First request: ~30 seconds (model downloads)
   - Subsequent requests: <1 second
   - Memory usage: ~450-480MB ✅

---

## 🎯 For Recruiters/Demos

The `optimize` branch provides a **professional live demo** experience:
- Fast startup
- Responsive search
- Works on free hosting
- Perfect for portfolio projects

---

**Built by Ali Asgar Momin**

