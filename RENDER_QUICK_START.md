# Render Deployment Quick Start

## 🚀 Quick Deployment Steps

Follow these steps in order to deploy your Property Broker AI app on Render.

### Prerequisites
✅ GitHub account with your repo pushed  
✅ Render account (free at https://render.com)  
✅ Environment variables ready

---

## 📋 Deployment Checklist

Copy this checklist and check off as you go:

### 1. Prepare Code
- [ ] Commit all changes to GitHub: `git add . && git commit -m "ready for deployment" && git push`
- [ ] Verify `.env.example` exists with all required variables
- [ ] Check `requirements.txt` has all dependencies

### 2. Create Database
- [ ] Go to Render → New → PostgreSQL
- [ ] Name: `broker-db`
- [ ] Region: Choose your region
- [ ] Click Create
- [ ] **COPY** the Internal Connection String

### 3. Deploy Backend
- [ ] Go to Render → New → Web Service
- [ ] Select your GitHub repo
- [ ] Name: `broker-backend`
- [ ] Region: Same as database
- [ ] Runtime: Python 3
- [ ] Build Command: `pip install -r requirements.txt && cd backend/core && python manage.py migrate && python manage.py collectstatic --noinput`
- [ ] Start Command: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
- [ ] Scroll down → Click "Advanced"
- [ ] Add Environment Variables (table below)
- [ ] Click Create Web Service
- [ ] Wait 5-10 minutes for deployment
- [ ] Copy the URL (e.g., `broker-backend.onrender.com`)

**Environment Variables for Backend:**

```
DEBUG=False
SECRET_KEY=<generate strong random string>
DATABASE_URL=<paste PostgreSQL connection string>
REDIS_URL=<your existing Redis URL>
GROQ_API_KEY=<your API key>
SERPAPI_API_KEY=<your API key>
PYTHONUNBUFFERED=1
PYTHON_VERSION=3.12.4
```

### 4. Deploy Frontend
- [ ] Go to Render → New → Static Site
- [ ] Select your GitHub repo
- [ ] Name: `broker-frontend`
- [ ] Branch: main
- [ ] Build Command: `cd frontend && npm install && npm run build`
- [ ] Publish Directory: `frontend/dist`
- [ ] Click "Advanced"
- [ ] Add Environment Variable:
  ```
  VITE_API_URL=https://broker-backend.onrender.com
  ```
- [ ] Click Create
- [ ] Wait 3-5 minutes
- [ ] Copy the URL (e.g., `broker-frontend.onrender.com`)

### 5. Update CORS (Backend)
- [ ] Go back to broker-backend service
- [ ] Click Environment tab
- [ ] Add: `FRONTEND_URL=https://broker-frontend.onrender.com`
- [ ] Click "Manual Deploy" → "Deploy latest commit"
- [ ] Wait for redeploy

### 6. Test Your App
- [ ] Open `https://broker-frontend.onrender.com` in browser
- [ ] Try selecting a locality
- [ ] Try creating a chat
- [ ] Check messages work
- [ ] Open admin: `https://broker-backend.onrender.com/admin/`

### 7. (Optional) Deploy Celery Worker
- [ ] Go to Render → New → Background Worker
- [ ] Name: `broker-worker`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `cd backend/core && celery -A core worker -l info`
- [ ] Add same environment variables as backend
- [ ] Click Create

---

## 🔧 Useful Links

| Link | Purpose |
|------|---------|
| https://render.com/docs | Render Documentation |
| https://broker-backend.onrender.com/admin/ | Admin Panel |
| https://broker-frontend.onrender.com | Your Live App |

---

## ⚠️ Troubleshooting

### Backend shows "503 Service Unavailable"
→ Check the Logs tab in Render  
→ Look for Python errors  
→ Common issues: missing environment variable, database migration failed

### Frontend shows blank page / 404
→ Check browser console (F12)  
→ Look for API errors  
→ Verify `VITE_API_URL` is correct in environment  
→ Try hard refresh (Ctrl+Shift+R)

### Chat/API not working
→ Go to Django admin  
→ Check if Chat table exists (it should after migration)  
→ Verify backend has correct `DATABASE_URL`  
→ Verify frontend `VITE_API_URL` has no trailing slash

### Images not loading
→ In production, you need cloud storage (S3)  
→ For now, use database/API for storing image references

---

## 💾 After Deployment

1. **Create Admin User**: 
   - In Render, go to broker-backend → Shell
   - Run: `python backend/core/manage.py createsuperuser`
   - Follow prompts

2. **Monitor**: Check Render dashboard for errors/performance

3. **Backup**: Render PostgreSQL has automatic backups

4. **Custom Domain**: Go to service settings → add domain

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- React/Vite: https://vitejs.dev

Good luck with your deployment! 🎉
