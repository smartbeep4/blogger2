# Blogger2 - Full-Stack Blog Platform

A production-ready blog platform built with Flask backend and React frontend, deployed on Render's free tier.

## Features

- **User Roles**: Admin, Editor, and Author with role-based access control
- **Rich Text Editor**: Quill editor with autosave functionality
- **Content Management**: Draft/publish workflow with categories and tags
- **Media Library**: ImageKit integration for image and video uploads
- **Search**: Full-text search across posts
- **Analytics**: Dashboard with view tracking and popular posts
- **Security**: JWT authentication, rate limiting, input validation, HTML sanitization

## Tech Stack

### Backend

- Flask 3.0
- PostgreSQL
- SQLAlchemy ORM
- Flask-JWT-Extended
- ImageKit for media storage

### Frontend

- React 18
- Vite 5
- React Router 6
- React Quill
- Axios

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL

### Backend Setup

1. Create a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp ../.env.example ../.env
# Edit .env with your configuration
```

4. Initialize the database:

```bash
flask db upgrade
```

5. Run the development server:

```bash
python run.py
```

### Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Deployment

See the [deployment guide](/home/smart/.claude/plans/quizzical-waddling-toucan.md) for detailed instructions on deploying to Render.

## License

MIT
