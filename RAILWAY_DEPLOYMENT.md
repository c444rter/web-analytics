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
     - Leave the "Custom Start Command" empty (it will use the command from nixpacks.toml)
     - Remove any "Pre-deploy step" (migrations are bypassed)

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
     - Leave the "Custom Start Command" empty
     - Set "Nixpacks Config Path" to `nixpacks.worker.toml`
     - Remove any "Pre-deploy step" (migrations are bypassed)

### 2. Environment Variables

Make sure to set these environment variables in both the Web API and Worker services:

- `DATABASE_URL`: Your Postgres connection string
- `REDIS_PUBLIC_URL`: Your Redis connection string
- `SECRET_KEY`: Your application secret key
- `SUPABASE_URL` and `SUPABASE_KEY`: If you're using Supabase

### 3. Deployment Configuration

The application uses four key files for deployment:

1. **Procfile**: Defines the commands to run for each service:
   ```
   web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
   worker: cd backend && rq worker --with-scheduler --url ${REDIS_PUBLIC_URL} --name worker-${RAILWAY_SERVICE_ID:-local} --verbose --worker-ttl 3600 --job-timeout 3600 --burst-delay 1 --max-jobs 0
   # Migrations are completely bypassed for this deployment since the database tables already exist
   # release: cd /app && PYTHONPATH=. alembic stamp head && PYTHONPATH=. alembic upgrade head
   ```

2. **nixpacks.toml**: Controls the build process for the Web API service:
   ```toml
   [phases.build]
   cmds = [
     "pip install -r requirements.txt"
   ]

   # Directly specify the start command
   [start]
   cmd = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
   ```

3. **nixpacks.worker.toml**: Controls the build process for the Worker service:
   ```toml
   [phases.build]
   cmds = [
     "pip install -r requirements.txt"
   ]

   # Directly specify the start command for the worker
   [start]
   cmd = "cd backend && rq worker --with-scheduler --url ${REDIS_PUBLIC_URL} --name worker-${RAILWAY_SERVICE_ID:-local} --verbose --worker-ttl 3600 --job-timeout 3600 --burst-delay 1 --max-jobs 0"
   ```

4. **Dockerfile**: Defines how to build the application:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app/backend
   COPY requirements.txt /app/requirements.txt
   RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt
   COPY . /app
   ENV PYTHONUNBUFFERED=1
   ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
   # IMPORTANT: Do NOT run migrations here
   # Migrations are completely bypassed for this deployment
   # since the database tables already exist
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### 4. Why This Configuration Works

This configuration solves the migration issues by:

1. **Completely Bypassing Migrations**: Since the database tables already exist, we don't need to run migrations at all
2. **Nixpacks Configuration**: The nixpacks.toml file explicitly defines the build and start commands, preventing Railway from automatically adding migration steps during the build phase
3. **Commented Out Release Command**: The release command in the Procfile is commented out to prevent migrations from running
4. **No Pre-deploy Steps**: All pre-deploy steps that would run migrations are removed
5. **Start Command**: Uses your Procfile to start the service

The key insights are:
1. Railway was trying to run migrations during the build phase, which was causing errors
2. Since the database tables already exist, there's no need to run migrations at all
3. By completely bypassing migrations, we avoid any potential conflicts with existing tables
4. This approach is simpler and more reliable for an existing database
5. For future schema changes, you can manually run migrations locally or through a separate process

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
