# Use Python 3.11 as base image
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend and build it
COPY frontend/ frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

# Copy backend code
WORKDIR /app
COPY backend/ backend/

# Database migrations will be run at startup

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run
ENV FLASK_ENV=production

# Start the application (run migrations first, then start gunicorn)
CMD cd backend && python migrate.py && gunicorn -w 1 -b 0.0.0.0:5000 run:app
