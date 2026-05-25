# Deployment Guide - Property Broker AI on Render

## Prerequisites
- Render account (create at https://render.com)
- GitHub repository with your code pushed
- Environment variables ready

## Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com and sign up
2. Click "New +" → "GitHub"
3. Connect your GitHub account
4. Select your repository

## Step 3: Create PostgreSQL Database on Render

1. In Render Dashboard: Click "New +" → "PostgreSQL"
2. Fill in:
   - **Name**: `broker-db`
   - **Database**: `broker_db`
   - **User**: `broker_user`
   - **Region**: Choose closest to you (e.g., Ohio, Virginia)
   - **Plan**: Free tier
3. Click "Create Database"
4. **Copy the Internal Connection String** (you'll need it)

## Step 4: Deploy Django Backend

1. Click "New +" → "Web Service"
2. Select your repository
3. Fill in settings:
   - **Name**: `broker-backend`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Build Command**: `pip install -r backend/requirements.txt && cd backend/core && python manage.py migrate && python manage.py collectstatic --noinput && python create_admin.py`
   - **Start Command**: `cd backend/core && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
   - **Plan**: Free tier

4. Click "Advanced" → Add Environment Variables:

| Key | Value |
|-----|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | (Generate a new secure key) |
| `DATABASE_URL` | (Paste PostgreSQL connection string from Step 3) |
| `REDIS_URL` | (Your existing remote Redis URL) |
| `GROQ_API_KEY` | (Your API key from .env) |
| `SERPAPI_API_KEY` | (Your API key from .env) |
| `ADMIN_USERNAME` | `admin` (or your preferred username) |
| `ADMIN_PASSWORD` | (Generate a strong password) |
| `ADMIN_EMAIL` | `admin@yoursite.com` |
| `PYTHONUNBUFFERED` | `1` |
| `PYTHON_VERSION` | `3.12.4` |

5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. **Copy the backend URL** (e.g., `broker-backend.onrender.com`)

## Step 5: Update Frontend Configuration

1. In your project, update `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  define: {
    __API_URL__: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8000'),
  }
})
```

2. Update `frontend/src/App.jsx` (or create API utility file):

Replace API calls from `http://localhost:8000` to use environment variable:

```javascript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// In your axios calls:
axios.get(`${API_BASE}/api/localities/`);
```

3. Update `frontend/package.json` - ensure you have a build script:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

## Step 6: Deploy React Frontend

1. In Render: Click "New +" → "Static Site"
2. Fill in:
   - **Name**: `broker-frontend`
   - **Repository**: Your repo
   - **Branch**: `main`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

3. Click "Advanced" → Add Environment Variables:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://broker-backend.onrender.com` |

4. Click "Create Static Site"
5. Wait for deployment (3-5 minutes)
6. **Copy the frontend URL** (e.g., `broker-frontend.onrender.com`)

## Step 7: Update Backend CORS Settings

1. Go to broker-backend service
2. Click "Environment" tab
3. Add/Update:
   - `FRONTEND_URL`: `https://broker-frontend.onrender.com`

4. Redeploy the service (click "Manual Deploy" → "Deploy latest commit")

## Step 8: Update Frontend with Backend URL

1. Go to broker-frontend service
2. Click "Environment" tab
3. Update:
   - `VITE_API_URL`: `https://broker-backend.onrender.com`

4. Trigger redeploy by pushing a commit or clicking "Manual Deploy"

## Step 9: Configure Celery Worker (FREE Option - GitHub Actions)

**⚠️ IMPORTANT**: The Celery worker is REQUIRED for the AI pipeline. Render Background Workers are paid, so we use **GitHub Actions** (FREE) to process tasks.

### How It Works:
- GitHub Actions runs every 5 minutes
- Picks up queued tasks from Redis
- Processes them (Groq LLM analysis, etc.)
- Returns results to database

### Setup:

1. **Add Secrets to GitHub Repository**:
   - Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
   - Click **"New repository secret"** and add:

   | Secret Name | Value |
   |------------|-------|
   | `DATABASE_URL` | PostgreSQL connection string from Render |
   | `REDIS_URL` | Your remote Redis URL |
   | `GROQ_API_KEY` | From your .env |
   | `SERPAPI_API_KEY` | From your .env |
   | `SECRET_KEY` | Same as Render backend |

2. **Workflow is Already Set Up**:
   - File: `.github/workflows/celery-worker.yml`
   - Runs automatically every 5 minutes
   - Or manually trigger from GitHub Actions tab

3. **Monitor Executions**:
   - Go to GitHub repo → **Actions** tab
   - Click **"Celery Worker - Process Tasks"**
   - View logs to see task processing

### Task Processing Timeline:
- User selects locality → Task queued to Redis
- GitHub Actions runs (every 5 min) → Processes task
- AI analysis completes → Frontend displays results
- Total delay: 0-5 minutes (acceptable for UX)

**Advantages:**
- ✅ Completely FREE
- ✅ No additional services needed
- ✅ Works with existing Redis
- ✅ Easy to monitor in GitHub

## Step 10: Final Testing

1. Go to your frontend URL: `https://broker-frontend.onrender.com`
2. Test:
   - ✅ Localities load
   - ✅ Properties display
   - ✅ Click "Contact Admin" button
   - ✅ Send a message
   - ✅ Message appears in chat

## Step 11: Access Django Admin Panel

Your superuser account was created automatically during deployment!

1. Go to: `https://broker-backend.onrender.com/admin/`
2. Login with credentials:
   - **Username**: `ADMIN_USERNAME` environment variable (default: `admin`)
   - **Password**: `ADMIN_PASSWORD` environment variable you set during deployment

3. From admin panel you can:
   - View/manage properties, localities, chats
   - Create new properties
   - View chat messages
   - Manage users

**Note**: The superuser credentials are stored securely in Render environment variables.

## Troubleshooting

### Backend shows errors
- Check "Logs" tab in Render dashboard
- Common issues:
  - Database not migrated: Check build command
  - Static files missing: Run `collectstatic`
  - Environment variables not set

### Frontend shows blank page
- Open browser console (F12)
- Check for API errors
- Verify `VITE_API_URL` points to correct backend URL
- Check if requests have CORS errors

### Chat not working
- Verify `DATABASE_URL` environment variable
- Check if tables exist: Use Django admin at `backend-url/admin`
- Login with superuser (create with `python manage.py createsuperuser`)

### AI Pipeline/Locality Analysis Not Working
- **Trigger analysis**: When you select a locality on the frontend, it should automatically queue the task
- **Check Celery worker**: Go to GitHub repo → **Actions** tab → **"Celery Worker - Process Tasks"** → check logs
- Verify `REDIS_URL` is set in GitHub Secrets
- Verify `GROQ_API_KEY` is set in GitHub Secrets
- Look for "Connected to redis://" in the GitHub Actions logs

### Manually Enrich Localities

If GitHub Actions isn't processing tasks, manually enrich:

```bash
# SSH into Render backend or use shell command:
cd backend/core

# Enrich all localities without analysis:
python manage.py enrich_localities

# Enrich specific locality:
python manage.py enrich_localities --id=1

# Force re-enrich all (including already analyzed):
python manage.py enrich_localities --all
```

This queues tasks to Redis. GitHub Actions will pick them up within 5 minutes.

### To Monitor Celery Tasks
```bash
# Via Django shell (optional):
from celery.result import AsyncResult
from properties.tasks import enrich_locality_pipeline

# Check task status:
result = AsyncResult('task-id')
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
print(result.result)  # Task output
```

### Images not uploading
- Check `MEDIA_ROOT` and `MEDIA_URL` in Django settings
- Use cloud storage (S3) for production images

## Production Checklist

- [ ] Change `DEBUG = False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` correctly
- [ ] Use PostgreSQL (not SQLite)
- [ ] Use Gunicorn/production server
- [ ] Set up HTTPS (Render does this automatically)
- [ ] Configure CORS for frontend domain
- [ ] **Deploy Celery worker** (REQUIRED for AI pipeline)
- [ ] Verify Celery worker can connect to Redis
- [ ] Test all features end-to-end (especially locality analysis)
- [ ] Set up monitoring/alerts
- [ ] Backup database regularly

## Useful Commands

```bash
# Connect to PostgreSQL database
psql postgresql://user:password@host:port/database

# View Django logs on Render
# (Use Render dashboard Logs tab)

# Manually trigger migration
# (Use Render dashboard - Manual Deploy)

# Create superuser in production
# (Via Render shell or management command)
```

## Next Steps

1. **Custom Domain**: Go to service settings → add custom domain
2. **SSL Certificate**: Render auto-provides free SSL
3. **Monitor Performance**: Use Render dashboard analytics
4. **Scale**: Upgrade plan as traffic grows

---

**Questions?** Check Render docs: https://render.com/docs
