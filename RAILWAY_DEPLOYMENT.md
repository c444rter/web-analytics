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
   - In the **Source** section:
     - Set the "Root Directory" to `/` (project root)
   - In the **Build** section:
     - Ensure "Builder" is set to use the Dockerfile (backend/Dockerfile)
   - In the **Deploy** section:
     - Set "Custom Start Command" to `web`

3. **Worker Service**:
   - Connect to the same GitHub repository
   - In the **Source** section:
     - Set the "Root Directory" to `/` (project root)
   - In the **Build** section:
     - Ensure "Builder" is set to use the Dockerfile (backend/Dockerfile)
   - In the **Deploy** section:
     - Set "Custom Start Command" to `worker`

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

### 5. Important Build Settings

To prevent migration errors during the build phase:

1. In the **Build** section:
   - If you see a "Custom Build Command" option, leave it empty or do not add one
   - This prevents Railway from running custom build commands that might interfere with the migration process

2. If you're still seeing migration errors:
   - Check if there's a `railway.toml` file in your repository that might be defining a custom build command
   - If found, either remove it or ensure it doesn't include migration commands

### 6. Troubleshooting

If you encounter issues with migrations:

1. Make sure the `alembic.ini` file is in the root directory
2. Ensure the `PYTHONPATH=..` is included in the release command
3. Check that the migrations are not being run during the build phase
4. Look at the build logs to see exactly where the error is occurring
5. If you see an error like `FAILED: No config file 'alembic.ini' found`, it means the build process is trying to run migrations but can't find the configuration file

## Notes

- The `release` command runs before both the web and worker services start
- Both services use the same Docker image but different start commands
- Railway automatically handles scaling and restarts
