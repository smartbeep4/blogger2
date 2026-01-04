# Deployment Guide: Render Free Tier

This guide walks you through deploying your full-stack blog platform to Render's free tier with zero cost.

## Overview

- **Backend**: Flask API with PostgreSQL database
- **Frontend**: React (Vite) served by Flask
- **Total Cost**: $0/month (using free tier)
- **Limitations**: Database expires after 90 days (requires renewal), service spins down after 15 minutes of inactivity

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Render account (sign up at https://render.com)
3. ImageKit account for media storage (sign up at https://imagekit.io)

## Step 1: Prepare Your Repository

Ensure the following files are committed to your GitHub repository:

- `backend/` - All Flask backend code
- `frontend/` - All React frontend code
- `requirements.txt` - Python dependencies (in backend/ or root)
- `render.yaml` - Render blueprint configuration
- `.gitignore` - Excluding venv, node_modules, .env, etc.

## Step 2: Set Up ImageKit (Media Storage)

1. Go to https://imagekit.io and sign up for a free account
2. After signup, go to the Dashboard
3. Copy the following credentials (you'll need these later):
   - **Public Key**
   - **Private Key**
   - **URL Endpoint** (looks like: https://ik.imagekit.io/your_id)

**Free Tier Limits:**

- 20GB storage
- 20GB bandwidth per month
- Sufficient for most blogs

## Step 3: Create PostgreSQL Database on Render

1. Log into Render dashboard (https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `blogger2-db` (or any name)
   - **Database**: `blogger2`
   - **User**: (auto-generated)
   - **Region**: Oregon (or nearest to you)
   - **PostgreSQL Version**: 16 (latest)
   - **Plan**: **Free**
4. Click **Create Database**
5. Wait for provisioning (1-2 minutes)
6. Once ready, go to the **Connect** tab
7. **Copy the Internal Database URL** (starts with `postgresql://`)
   - Format: `postgresql://user:password@host/database`
   - Save this - you'll need it for the web service

**Important Notes:**

- Free PostgreSQL databases expire after 90 days
- You'll receive an email before expiration
- Data can be exported/imported or you can renew the database

## Step 4: Create Web Service on Render

### Option A: Using render.yaml Blueprint (Recommended)

1. In Render dashboard, click **New +** → **Blueprint**
2. Connect your GitHub repository
3. Render will detect `render.yaml` and show the services:
   - PostgreSQL database
   - Web service
4. Click **Apply**
5. Render will create both services automatically
6. Skip to **Step 5: Configure Environment Variables**

### Option B: Manual Setup

1. In Render dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `blogger2` (or any name)
   - **Region**: Oregon (same as database)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && cd .. && flask db upgrade
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn -w 1 -b 0.0.0.0:$PORT run:app
     ```
   - **Plan**: **Free**
4. Click **Create Web Service**

## Step 5: Configure Environment Variables

1. Go to your web service in Render dashboard
2. Click on **Environment** tab
3. Add the following environment variables:

| Key                     | Value                           | Notes                     |
| ----------------------- | ------------------------------- | ------------------------- |
| `PYTHON_VERSION`        | `3.11.0`                        | Python version            |
| `FLASK_APP`             | `backend/run.py`                | Flask entry point         |
| `FLASK_ENV`             | `production`                    | Environment               |
| `SECRET_KEY`            | (Generate random string)        | Use password generator    |
| `JWT_SECRET_KEY`        | (Generate random string)        | Different from SECRET_KEY |
| `DATABASE_URL`          | (Paste from Step 3)             | Internal Database URL     |
| `IMAGEKIT_PRIVATE_KEY`  | (From Step 2)                   | ImageKit private key      |
| `IMAGEKIT_PUBLIC_KEY`   | (From Step 2)                   | ImageKit public key       |
| `IMAGEKIT_URL_ENDPOINT` | (From Step 2)                   | ImageKit URL endpoint     |
| `CORS_ORIGINS`          | `https://blogger2.onrender.com` | Your Render URL           |

**To generate SECRET_KEY and JWT_SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Run this command twice to get two different keys.

4. Click **Save Changes**
5. Render will automatically redeploy with the new environment variables

## Step 6: Wait for Deployment

1. Monitor the **Logs** tab to see deployment progress
2. The build process will:
   - Install Python dependencies
   - Install Node.js dependencies
   - Build React frontend
   - Run database migrations
   - Start Gunicorn server
3. First deployment takes 5-10 minutes
4. Once you see "Listening at: http://0.0.0.0:10000", deployment is complete

## Step 7: Create Admin User

1. Go to your web service in Render dashboard
2. Click on **Shell** tab (opens a terminal)
3. Run the following commands:

```bash
cd backend
flask shell
```

4. In the Flask shell, create an admin user:

```python
from app import db
from app.models.user import User

admin = User(
    username='admin',
    email='your-email@example.com',
    display_name='Admin',
    role='admin'
)
admin.set_password('your-secure-password')
db.session.add(admin)
db.session.commit()
print(f"Admin user created: {admin.username}")
exit()
```

Replace:

- `your-email@example.com` with your actual email
- `your-secure-password` with a strong password (at least 8 characters)

## Step 8: Test Your Deployment

1. Open your Render URL (e.g., `https://blogger2.onrender.com`)
2. You should see the React frontend
3. Click **Login** and sign in with your admin credentials
4. Create a test post, add categories/tags, test the editor

**Test Checklist:**

- ✅ Frontend loads without errors
- ✅ Login works
- ✅ Can create/edit/delete posts
- ✅ Autosave works (wait 2 seconds after typing)
- ✅ Categories and tags work
- ✅ Image upload to ImageKit works
- ✅ Search functionality works
- ✅ Public post viewing works (without login)

## Step 9: Configure Custom Domain (Optional)

1. Go to your web service in Render dashboard
2. Click **Settings** → **Custom Domain**
3. Add your domain (e.g., `blog.yourdomain.com`)
4. Follow Render's DNS configuration instructions
5. Update `CORS_ORIGINS` environment variable to include your custom domain:
   ```
   https://blog.yourdomain.com
   ```

## Maintenance

### Monitoring

- **Logs**: Check the Logs tab regularly for errors
- **Metrics**: View CPU/Memory usage in the Metrics tab
- **Uptime**: Free tier services spin down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds
  - Consider using a service like UptimeRobot for periodic pings

### Database Renewal (Every 90 Days)

1. Export data before expiration:

   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

2. Create a new free PostgreSQL database

3. Import data:

   ```bash
   psql $NEW_DATABASE_URL < backup.sql
   ```

4. Update `DATABASE_URL` environment variable

### Updating Your Application

1. Push changes to your GitHub repository
2. Render will automatically detect and redeploy
3. Monitor the Logs tab during deployment

## Troubleshooting

### Build Failures

**Error: "Requirements installation failed"**

- Check `requirements.txt` syntax
- Ensure all dependencies are compatible with Python 3.11

**Error: "npm install failed"**

- Check `package.json` syntax
- Clear build cache: Settings → Build & Deploy → Clear build cache

**Error: "Migration failed"**

- Check database connection (DATABASE_URL)
- Manually run migrations in Shell:
  ```bash
  cd backend
  flask db upgrade
  ```

### Runtime Errors

**Error: "Connection refused" (Database)**

- Verify DATABASE_URL is correct
- Check database is running in Render dashboard

**Error: "CORS policy error"**

- Verify CORS_ORIGINS matches your Render URL
- Check browser console for exact origin

**Error: "JWT decode error"**

- Verify JWT_SECRET_KEY is set
- Clear browser cookies and localStorage
- Try logging in again

**Error: "ImageKit upload failed"**

- Verify ImageKit credentials are correct
- Check ImageKit dashboard for usage limits

### Performance Issues

**Slow first request (cold start)**

- Free tier services spin down after 15 minutes
- First request takes 30-60 seconds to wake up
- This is normal behavior for free tier

**Database query timeouts**

- Add indexes to frequently queried fields
- Optimize N+1 queries with eager loading
- Consider upgrading to paid tier if needed

## Cost Optimization

### Staying on Free Tier

- **Database**: Renew every 90 days (free)
- **Web Service**: 750 hours/month (sufficient for single service)
- **Media**: Use ImageKit free tier (20GB storage, 20GB bandwidth)
- **Total**: $0/month

### When to Upgrade

Consider upgrading if you experience:

- Consistent database size over 1GB
- More than 20GB media bandwidth per month
- Need for 99.9% uptime (no spin-down)
- Multiple concurrent users causing performance issues

**Paid Plans:**

- PostgreSQL: $7/month (10GB storage, no expiration)
- Web Service: $7/month (512MB RAM, no spin-down)
- Total: $14/month for production-ready setup

## Security Checklist

Before going live:

- ✅ Strong SECRET_KEY and JWT_SECRET_KEY
- ✅ CORS_ORIGINS restricted to your domain only
- ✅ Admin user has strong password
- ✅ Database URL is not exposed in logs
- ✅ ImageKit credentials are secure
- ✅ HTTPS enabled (automatic on Render)
- ✅ Rate limiting configured (already in code)
- ✅ Input validation enabled (already in code)
- ✅ HTML sanitization enabled (already in code)

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **ImageKit Docs**: https://docs.imagekit.io

## Summary

Your blog platform is now live on Render's free tier! Here's what you have:

- ✅ Full-stack blog with Flask + React
- ✅ PostgreSQL database (1GB, renew every 90 days)
- ✅ Rich text editor with autosave
- ✅ Role-based access control (Admin, Editor, Author)
- ✅ Media storage on ImageKit (20GB)
- ✅ HTTPS enabled
- ✅ Automatic deploys from GitHub
- ✅ Zero monthly cost

Next steps:

1. Create categories and tags
2. Invite editors and authors
3. Start writing content
4. Share your blog with the world!
