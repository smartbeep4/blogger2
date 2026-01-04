# Blogger2 Setup Guide

Complete setup instructions for the Blogger2 blog platform.

## What's Been Built

### ✅ Backend (Flask)

- **Flask App Factory** with production-ready configuration
- **User Authentication** - JWT-based auth with register, login, refresh token
- **Role-Based Access Control (RBAC)** - Admin, Editor, Author roles
- **Database Models**:
  - User (with password hashing)
  - Post (with categories, tags, status)
  - Category & Tag (many-to-many relationships)
  - Media (ImageKit integration)
  - PageView (analytics tracking)
  - AutosaveDraft (editor autosave)
- **API Routes**: Auth endpoints with validation and rate limiting
- **Security**: Input validation, rate limiting, password hashing, JWT tokens

### ✅ Frontend (React + Vite)

- **Vite Configuration** with React plugin
- **Axios API Client** with JWT interceptors and automatic token refresh
- **AuthContext** for global authentication state
- **AuthService** for all auth operations
- **React Router** setup with protected routes
- **Base CSS** with utility classes

### ✅ Deployment

- **render.yaml** for one-click Render deployment
- **Environment configuration** for dev/staging/production

## Prerequisites

### Required

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **PostgreSQL** (for production) or SQLite (for development)
- **Git**

### Optional

- **ImageKit Account** (free tier) for media storage

## Local Development Setup

### 1. Install System Dependencies (WSL/Ubuntu)

```bash
# Update package list
sudo apt update

# Install Python development tools
sudo apt install python3.10 python3.10-venv python3-pip

# Install PostgreSQL (optional - can use SQLite for development)
sudo apt install postgresql postgresql-contrib

# Verify installations
python3 --version
node --version
npm --version
```

### 2. Backend Setup

```bash
cd /mnt/c/Users/simon/Code/blogger2/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp ../.env.example ../.env
```

Edit `.env` and configure:

```bash
# For local development with SQLite (easiest)
DATABASE_URL=sqlite:///blogger2.db

# OR for PostgreSQL
DATABASE_URL=postgresql://localhost:5432/blogger2

# Set development secrets (these are fine for local dev)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
FLASK_ENV=development

# ImageKit (leave empty for now, add when testing media upload)
IMAGEKIT_PRIVATE_KEY=
IMAGEKIT_PUBLIC_KEY=
IMAGEKIT_URL_ENDPOINT=
```

### 4. Initialize Database

```bash
# Still in backend directory with venv activated
export FLASK_APP=run.py

# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration with all models"

# Apply migration
flask db upgrade
```

### 5. Create Admin User (Optional)

```bash
# Open Flask shell
flask shell

# Create admin user
from app import db
from app.models.user import User

admin = User(
    username='admin',
    email='admin@test.com',
    role='admin',
    display_name='Admin User'
)
admin.set_password('password123')
db.session.add(admin)
db.session.commit()
print(f"Created admin user: {admin.username}")
exit()
```

### 6. Run Backend Server

```bash
# Still in backend directory
python run.py
```

Backend will run on `http://localhost:5000`

### 7. Frontend Setup

Open a **new terminal**:

```bash
cd /mnt/c/Users/simon/Code/blogger2/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### 8. Test the Application

#### Test Backend API:

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Test Frontend:

1. Open `http://localhost:5173` in your browser
2. The React app should load with routing
3. Try navigating to `/login`, `/register`

## Production Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. **Commit all code to GitHub**:

```bash
git add .
git commit -m "Initial blog platform implementation"
git push origin main
```

2. **Sign up/Login to Render**: https://render.com

3. **Create New Blueprint**:
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

4. **Configure Environment Variables** in Render Dashboard:
   - `IMAGEKIT_PRIVATE_KEY` - From imagekit.io dashboard
   - `IMAGEKIT_PUBLIC_KEY` - From imagekit.io dashboard
   - `IMAGEKIT_URL_ENDPOINT` - From imagekit.io dashboard
   - `CORS_ORIGINS` - Update to your actual Render URL

5. **Wait for Deployment** (5-10 minutes first time)

6. **Create Admin User** via Render Shell:
   - Go to your web service → "Shell"
   - Run:

```python
cd backend
flask shell
from app import db
from app.models.user import User
admin = User(username='admin', email='admin@yourdomain.com', role='admin')
admin.set_password('your-secure-password')
db.session.add(admin)
db.session.commit()
exit()
```

### Option 2: Manual Render Setup

#### Step 1: Create PostgreSQL Database

1. Render Dashboard → "New" → "PostgreSQL"
2. Name: `blogger2-db`
3. Plan: Free
4. Region: Oregon (or nearest)
5. Create → **Copy Internal Database URL**

#### Step 2: Create Web Service

1. Render Dashboard → "New" → "Web Service"
2. Connect GitHub repository
3. Configure:
   - **Name**: `blogger2`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Environment**: Python
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && cd .. && cd backend && flask db upgrade
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn -w 1 -b 0.0.0.0:$PORT run:app
     ```
   - **Plan**: Free

#### Step 3: Set Environment Variables

Add these in "Environment" tab:

```
PYTHON_VERSION=3.11.0
FLASK_APP=backend/run.py
FLASK_ENV=production
SECRET_KEY=[Use Render's "Generate" button]
JWT_SECRET_KEY=[Use Render's "Generate" button]
DATABASE_URL=[Paste Internal DB URL from Step 1]
IMAGEKIT_PRIVATE_KEY=[From imagekit.io]
IMAGEKIT_PUBLIC_KEY=[From imagekit.io]
IMAGEKIT_URL_ENDPOINT=[From imagekit.io]
CORS_ORIGINS=https://blogger2.onrender.com
RATELIMIT_STORAGE_URL=memory://
```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for build (5-10 minutes)
3. Access via your Render URL

## ImageKit Setup (Media Storage)

1. **Sign up**: https://imagekit.io
2. **Free Tier**: 20GB storage, 20GB bandwidth/month
3. **Get Credentials**:
   - Go to Dashboard → Developer Options → API Keys
   - Copy:
     - Private Key
     - Public Key
     - URL Endpoint
4. **Add to Environment Variables** (both local `.env` and Render)

## Project Structure Reference

```
blogger2/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Configuration
│   │   ├── models/               # Database models
│   │   │   ├── user.py
│   │   │   ├── post.py
│   │   │   ├── category.py
│   │   │   ├── tag.py
│   │   │   ├── media.py
│   │   │   └── analytics.py
│   │   ├── routes/               # API endpoints
│   │   │   ├── auth.py           # ✅ Implemented
│   │   │   ├── posts.py          # TODO
│   │   │   ├── users.py          # TODO
│   │   │   ├── media.py          # TODO
│   │   │   ├── categories.py     # TODO
│   │   │   ├── tags.py           # TODO
│   │   │   └── analytics.py      # TODO
│   │   ├── middleware/
│   │   │   └── rbac.py           # ✅ Implemented
│   │   ├── services/             # TODO
│   │   ├── validators/           # TODO
│   │   └── utils/                # TODO
│   ├── tests/                    # TODO
│   ├── migrations/               # Generated by Flask-Migrate
│   ├── requirements.txt          # ✅ Created
│   └── run.py                    # ✅ Created
├── frontend/
│   ├── src/
│   │   ├── main.jsx              # ✅ Created
│   │   ├── App.jsx               # ✅ Created (with routing)
│   │   ├── components/           # TODO: Implement components
│   │   ├── pages/                # TODO: Implement pages
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # ✅ Created
│   │   ├── hooks/                # TODO
│   │   ├── services/
│   │   │   ├── api.js            # ✅ Created
│   │   │   └── authService.js    # ✅ Created
│   │   └── styles/
│   │       └── index.css         # ✅ Created
│   ├── package.json              # ✅ Created
│   ├── vite.config.js            # ✅ Created
│   └── index.html                # ✅ Created
├── .env.example                  # ✅ Created
├── .gitignore                    # ✅ Created
├── render.yaml                   # ✅ Created
├── README.md                     # ✅ Created
└── SETUP.md                      # ✅ This file
```

## Next Steps to Complete the Application

### 1. Implement Remaining Backend Routes

- [ ] Posts CRUD (`backend/app/routes/posts.py`)
- [ ] User management (`backend/app/routes/users.py`)
- [ ] Media upload (`backend/app/routes/media.py`)
- [ ] Categories & Tags (`backend/app/routes/categories.py`, `tags.py`)
- [ ] Analytics (`backend/app/routes/analytics.py`)

### 2. Implement Frontend Components

- [ ] Login/Register forms
- [ ] Post list and detail views
- [ ] Quill editor with autosave
- [ ] Media library
- [ ] User dashboard
- [ ] Admin panel

### 3. Add Testing

- [ ] Backend tests with pytest
- [ ] Frontend tests with Vitest

### 4. Implement Search

- [ ] PostgreSQL full-text search
- [ ] Search UI

## Troubleshooting

### Backend won't start

- Check virtual environment is activated
- Verify all dependencies installed: `pip list`
- Check DATABASE_URL is correct
- Check Flask app can be found: `echo $FLASK_APP`

### Database migration errors

- Delete `migrations/` folder and start over
- Check database is running (for PostgreSQL)
- Verify DATABASE_URL format

### Frontend won't start

- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node version: `node --version` (should be 18+)

### CORS errors

- Check backend CORS_ORIGINS includes frontend URL
- Check both servers are running
- Check proxy configuration in `vite.config.js`

### Authentication not working

- Check JWT_SECRET_KEY is set
- Check tokens in browser localStorage
- Check API endpoints return correct status codes

## Free Tier Limits

### Render (Backend + Database)

- **Web Service**: Spins down after 15 min inactivity, 512MB RAM
- **PostgreSQL**: 1GB storage, expires after 90 days (renewable)
- **Cold Start**: ~30-60 seconds on first request after sleep

### ImageKit (Media)

- **Storage**: 20GB
- **Bandwidth**: 20GB/month
- **Transformations**: 1000/month

## Support

For issues or questions:

- Check the implementation plan: `/home/smart/.claude/plans/quizzical-waddling-toucan.md`
- Review Flask docs: https://flask.palletsprojects.com/
- Review React docs: https://react.dev/
- Review Vite docs: https://vitejs.dev/
