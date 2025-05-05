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
     - Set "Builder" to **Nixpacks**
     - Add a "Custom Build Command":
       ```
       pip install -r requirements.txt
       ```
   - In the **Deploy** section:
     - Set "Custom Start Command" to `web`
     - Add a "Pre-deploy step":
       ```
       cd /app && PYTHONPATH=. alembic current && PYTHONPATH=. alembic upgrade head
       ```

3. **Worker Service**:
   - Connect to the same GitHub repository
   - In the **Source** section:
     - Set the "Root Directory" to `/` (project root)
   - In the **Build** section:
     - Set "Builder" to **Nixpacks**
     - Add a "Custom Build Command":
       ```
       pip install -r requirements.txt
       ```
   - In the **Deploy** section:
     - Set "Custom Start Command" to `worker`
     - Add a "Pre-deploy step":
       ```
       cd /app && PYTHONPATH=. alembic current && PYTHONPATH=. alembic upgrade head
       ```

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
   release: cd /app && PYTHONPATH=. alembic current && PYTHONPATH=. alembic upgrade head
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
   # IMPORTANT: Do NOT run migrations here
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### 4. Why This Configuration Works

This configuration solves the migration issues by:

1. **Custom Build Command**: Overrides Railway's default build process, preventing it from trying to run migrations during the build phase
2. **Pre-deploy Step**: Runs migrations from the correct directory with the correct Python path
3. **Alembic Version Tracking**: Uses `alembic current` to check the current migration state before running `upgrade head`
4. **Start Command**: Uses your Procfile to start the service

The key insights are:
1. Railway was trying to run migrations during the build phase, but couldn't find the alembic.ini file because it was looking in the wrong directory
2. Even with the correct path, migrations would fail when tables already exist from previous deployments
3. By checking the current migration state first with `alembic current`, we ensure Alembic is aware of which migrations have already been applied
4. This approach leverages Alembic's built-in version tracking system, which is more reliable than trying to filter SQL statements

### 5. Troubleshooting

If you still encounter issues:

1. Check the build logs to see exactly where the error is occurring
2. Ensure the alembic.ini file is in the root directory
3. Verify that both services have identical build and pre-deploy configurations
4. Make sure there are no Railway configuration files in your repository (like railway.toml)

## Notes

- Both services should use the same build configuration but different start commands
- The pre-deploy step runs before both the web and worker services start
- Railway automatically handles scaling and restarts
