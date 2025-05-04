# Railway Deployment Guide

This guide explains how to deploy the web analytics application to Railway.

## Prerequisites

- A Railway account
- Git repository with the application code
- Environment variables set up in Railway

## Deployment Steps

### 1. Set Up Services in Railway

You need to set up three services in Railway:

1. **Redis Service**:
   - Use Railway's managed Redis service
   - Note the connection URL for use in other services

2. **Web API Service (mydavids)**:
   - Connect to your GitHub repository
   - Set the root directory to `/` (project root)
   - Set the start command to `web`
   - Enable "Use Procfile" option if available

3. **Worker Service**:
   - Connect to the same GitHub repository
   - Set the root directory to `/` (project root)
   - Set the start command to `worker`
   - Enable "Use Procfile" option if available

### 2. Environment Variables

Make sure to set these environment variables in both the Web API and Worker services:

- `DATABASE_URL`: Your Postgres connection string
- `REDIS_PUBLIC_URL`: Your Redis connection string
- `SECRET_KEY`: Your application secret key
- `SUPABASE_URL` and `SUPABASE_KEY`: If you're using Supabase

### 3. Deployment Configuration

The application uses two key files for deployment:

1. **Procfile**: Defines the commands to run for each service:
   ```
   web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
   worker: cd backend && rq worker --with-scheduler --url ${REDIS_PUBLIC_URL} --name worker-${RAILWAY_SERVICE_ID:-local} --verbose --worker-ttl 3600 --job-timeout 3600 --burst-delay 1 --max-jobs 0
   release: cd backend && PYTHONPATH=.. alembic upgrade head
   ```

2. **Dockerfile**: Defines how to build the application:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app/backend
   COPY requirements.txt /app/requirements.txt
   RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt
   COPY . /app
   ENV PYTHONUNBUFFERED=1
   ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### 4. Deployment Process

When you deploy to Railway:

1. Railway uses the Dockerfile to build the application
2. Before starting the service, Railway runs the `release` command from the Procfile
3. The release command runs database migrations
4. Railway then starts the service using the appropriate command from the Procfile

### 5. Troubleshooting

If you encounter issues with migrations:

1. Make sure the `alembic.ini` file is in the root directory
2. Ensure the `PYTHONPATH=..` is included in the release command
3. Check that the migrations are not being run during the build phase

## Notes

- The `release` command runs before both the web and worker services start
- Both services use the same Docker image but different start commands
- Railway automatically handles scaling and restarts
