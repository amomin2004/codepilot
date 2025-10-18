# 🚀 CodePilot Cloud Deployment Guide

Deploy CodePilot to the cloud with **Vercel (Frontend) + Render (Backend)** for free!

---

## 📋 **Prerequisites**

- GitHub account
- Vercel account (sign up at https://vercel.com)
- Render account (sign up at https://render.com)
- Your CodePilot repository pushed to GitHub

---

## 🔧 **Part 1: Deploy Backend to Render**

### **Step 1: Push to GitHub**

```bash
cd /Users/aliasgarmomin/codepilot
git add .
git commit -m "Add cloud deployment configuration"
git push origin main
```

### **Step 2: Create Render Service**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (`codepilot`)
4. Configure the service:

   **Settings:**
   - **Name:** `codepilot-api`
   - **Region:** Oregon (US West) - Free tier
   - **Branch:** `main`
   - **Root Directory:** Leave empty
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`

5. **Environment Variables:**
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Add these:
     ```
     PYTHONPATH=/opt/render/project/src
     PYTHONUNBUFFERED=1
     ```

6. Click **"Create Web Service"**

7. **Wait for deployment** (5-10 minutes for first deploy)

8. **Copy your API URL** (e.g., `https://codepilot-api.onrender.com`)

### **Step 3: Test Backend**

```bash
curl https://codepilot-api.onrender.com/health
```

Expected: `{"status":"healthy","timestamp":"..."}`

---

## 🎨 **Part 2: Deploy Frontend to Vercel**

### **Step 1: Prepare Frontend**

Update `web/.env.production` (create if doesn't exist):

```bash
NEXT_PUBLIC_API_URL=https://codepilot-api.onrender.com
```

Commit this:
```bash
git add web/.env.production
git commit -m "Add production API URL"
git push origin main
```

### **Step 2: Deploy to Vercel**

#### **Option A: Vercel CLI (Recommended)**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd web
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: codepilot
# - Directory: ./ (current)
# - Override settings? No
```

#### **Option B: Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `web`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

5. **Environment Variables:**
   - Click **"Environment Variables"**
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://codepilot-api.onrender.com
     ```

6. Click **"Deploy"**

7. **Wait for deployment** (2-3 minutes)

8. **Your app is live!** (e.g., `https://codepilot.vercel.app`)

---

## ✅ **Part 3: Test Your Deployment**

### **1. Test Frontend**
Visit your Vercel URL: `https://codepilot.vercel.app`

### **2. Index a Repository**
1. Go to **"Ingest"** page
2. Select **"GitHub URL"**
3. Enter: `https://github.com/facebook/react`
4. Click **"Start Indexing"**
5. Wait for completion (~10-30 seconds)

### **3. Search**
1. Go to **"Search"** page
2. Query: `How do I create a React component?`
3. View results!

---

## 🔄 **Part 4: Continuous Deployment**

Both Vercel and Render automatically redeploy on git push!

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# Automatic deployments trigger:
# ✅ Render: Backend updates automatically
# ✅ Vercel: Frontend updates automatically
```

---

## 🐛 **Troubleshooting**

### **Backend Issues**

#### **Problem: API returns 500 errors**
```bash
# Check Render logs
# Dashboard → Your Service → Logs
```

**Common fixes:**
- Ensure `requirements.txt` includes all dependencies
- Check Python version (should be 3.11+)
- Verify `PYTHONPATH` environment variable

#### **Problem: Model download fails**
The first request will download the embedding model (~80MB). This takes 20-30 seconds.

**Solution:** Wait patiently for first request!

### **Frontend Issues**

#### **Problem: Can't connect to API**
Check `NEXT_PUBLIC_API_URL` in Vercel environment variables.

**Fix:**
1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your Render URL
3. Redeploy

#### **Problem: CORS errors**
The backend already has CORS enabled for all origins. If issues persist:

```python
# In api/main.py, verify:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be "*" for public access
    ...
)
```

---

## 💰 **Cost Breakdown**

### **Free Tier Limits:**

**Render (Backend):**
- ✅ Free
- ⏱️ 750 hours/month
- 💾 512 MB RAM
- ⚠️ Sleeps after 15 min inactivity (wakes on request)

**Vercel (Frontend):**
- ✅ Free
- 🚀 100 GB bandwidth/month
- 📦 Unlimited requests
- ⚡ Global CDN

**Total Monthly Cost:** **$0** 🎉

---

## 🚀 **Performance Optimization**

### **Keep Backend Awake**

Render free tier sleeps after 15 minutes. Solutions:

#### **Option 1: Ping Service**
Use https://cron-job.org to ping your API every 14 minutes:
```
GET https://codepilot-api.onrender.com/health
```

#### **Option 2: Upgrade**
Render Starter plan ($7/month) keeps it always on.

### **Speed Up Model Loading**

The embedding model downloads on first run. To persist it:

1. Use Render Disk (paid feature)
2. Or accept 20-30s first load time

---

## 🔐 **Security (Optional)**

### **Add API Authentication**

To prevent abuse, add API key authentication:

1. **Add to `api/main.py`:**
```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "your-secret-key")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

2. **Add to Render environment:**
```
API_KEY=your-super-secret-key-here
```

3. **Update frontend API client:**
```typescript
// web/src/lib/api.ts
headers: {
  'X-API-Key': process.env.NEXT_PUBLIC_API_KEY,
}
```

---

## 📊 **Monitoring**

### **Render:**
- Dashboard → Your Service → Metrics
- View CPU, Memory, Request count

### **Vercel:**
- Dashboard → Your Project → Analytics
- View page views, load times, errors

---

## 🎯 **Next Steps**

1. ✅ Custom domain (both Vercel and Render support this)
2. ✅ Add rate limiting to prevent abuse
3. ✅ Set up monitoring alerts
4. ✅ Add analytics (PostHog, Google Analytics)
5. ✅ Enable HTTPS (automatic on both platforms)

---

## 📝 **Quick Reference**

### **Your URLs:**
- **Frontend:** `https://codepilot.vercel.app`
- **Backend:** `https://codepilot-api.onrender.com`
- **API Docs:** `https://codepilot-api.onrender.com/docs`

### **Important Commands:**
```bash
# Redeploy everything
git push origin main

# Vercel: Force redeploy
cd web && vercel --prod

# Check backend logs
# Visit: https://dashboard.render.com → Your Service → Logs
```

---

## 🎉 **You're Live!**

Your CodePilot is now accessible to anyone on the internet! Share your URL and let people search any GitHub repository with natural language! 🚀

**Example Usage:**
1. Visit `https://codepilot.vercel.app`
2. Click "Ingest"
3. Enter any GitHub URL
4. Search with natural language!

---

## 💡 **Pro Tips**

1. **First Load:** Backend may take 30s to wake up (Render free tier)
2. **Large Repos:** Indexing big repos may timeout on free tier
3. **Model Download:** First request downloads ~80MB model (one-time)
4. **Persistent Storage:** Index is rebuilt on each deployment (use Render Disk for persistence)

---

**Need help?** Check:
- Render Logs: https://dashboard.render.com
- Vercel Logs: https://vercel.com/dashboard
- GitHub Issues: Create an issue in your repo

**Happy Deploying! 🚀**

