# 🔄 How to Restart the API

After making code changes, you need to restart the API server for changes to take effect.

## If Running Manually

### Stop the server:
```bash
# Press Ctrl+C in the terminal where the API is running
```

### Start it again:
```bash
cd /Users/aliasgarmomin/codepilot
python3 api/main.py
```

## If Running in Background

### Find the process:
```bash
ps aux | grep "api/main.py"
```

### Kill it:
```bash
kill <PID>
```

### Start it again:
```bash
cd /Users/aliasgarmomin/codepilot
python3 api/main.py &
```

## If Running with Docker

```bash
docker-compose restart api
```

## Quick Check

After restarting, verify the GitHub URL support is working:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "https://github.com/octocat/Hello-World"}'
```

You should see:
- ✅ "Detected GitHub URL"
- ✅ "Cloning repository"
- ✅ "Repository cloned to /tmp/..."
- ✅ Successful ingestion

## Common Issues

### Issue: Still getting "Root path is not a directory" error
**Solution**: API wasn't restarted. Stop and start again.

### Issue: "Git is not installed"
**Solution**: Install git with `brew install git` (macOS) or your package manager.

### Issue: "Git clone failed"
**Solution**: Check if the repository URL is correct and public.

