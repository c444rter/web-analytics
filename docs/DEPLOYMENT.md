# Deployment Guide

This document provides detailed instructions for deploying the Shopify Analytics application using Supabase, Railway, and Vercel.

## Overview

The application is deployed using the following services:
- **Supabase**: Database and file storage
- **Railway**: Backend API and worker services
- **Vercel**: Frontend hosting

## 1. Supabase Setup

### Create a Supabase Project

1. Go to [Supabase](https://supabase.com/) and sign up or log in
2. Click "New Project"
3. Enter a name for your project (e.g., "web-analytics")
4. Create a secure database password (save this securely)
5. Choose the region closest to your users
6. Click "Create new project"

### Set Up Storage

1. In your Supabase dashboard, go to "Storage" in the left sidebar
2. Click "Create a new bucket"
3. Name it "uploads"
4. Choose "Private" for bucket type
5. Click "Create bucket"

### Configure Storage Permissions

1. Go to "Storage" → "Policies"
2. Click on the "uploads" bucket
3. Click "Add policy"
4. Select "Create a policy from scratch"
5. For "Policy name," enter "Allow authenticated uploads"
6. For "Allowed operations," select:
   - SELECT (allows reading files)
   - INSERT (allows uploading files)
   - UPDATE (allows updating files)
   - DELETE (allows deleting files)
7. For "Target roles," select "authenticated" (users who are logged in)
8. For "Policy definition," use this SQL:
   ```sql
   (bucket_id = 'uploads'::text) AND (auth.uid() = owner)
   ```
9. Click "Save policy"

### Get Connection Details

1. Go to "Project Settings" → "Database"
2. Copy the "Connection string" in URI format
3. Replace `[YOUR-PASSWORD]` with your database password
4. Go to "Project Settings" → "API"
5. Copy the "URL" and "anon" key
6. Save these details for the Railway setup

## 2. Railway Setup

### Create a Railway Account

1. Go to [Railway](https://railway.app/) and sign up or log in with GitHub

### Create a New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your web-analytics repository
4. If prompted, install the Railway GitHub app

### Configure the Backend API Service

1. Railway will detect your Dockerfile
2. **Important**: For the build context, you need to ensure requirements.txt is available
   - Set the root directory to the project root (where requirements.txt is located)
   - In the "Settings" tab, under "Service Settings", set "Service Path" to `/backend`
   - This ensures that the Dockerfile can find the requirements.txt file
3. Click "Deploy"
4. Wait for the initial deployment to complete
5. Go to the "Variables" tab and add the following environment variables:
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `SECRET_KEY`: Generate a random string
   - `NEXTAUTH_SECRET`: Generate another random string
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `BUCKET_NAME`: "uploads"
   - `REDIS_HOST`: This will be set automatically when you add Redis
   - `REDIS_PORT`: This will be set automatically when you add Redis
   - `REDIS_DB`: "0"
6. Go to the "Settings" tab
7. Under "Start Command", enter: `uvicorn main:app --host 0.0.0.0 --port $PORT`
8. Click "Deploy" to apply changes

### Add Redis to Your Project

1. In your project dashboard, click "New"
2. Select "Redis"
3. Railway will automatically provision a Redis instance
4. Wait for it to complete

### Set Up Worker Service

1. In your project dashboard, click "New"
2. Select "GitHub Repo"
3. Select the same repository
4. **Important**: Use the same build context settings as the API service
   - Set the root directory to the project root (where requirements.txt is located)
   - In the "Settings" tab, under "Service Settings", set "Service Path" to `/backend`
5. Click "Deploy"
6. Wait for the initial deployment to complete
7. Go to the "Variables" tab
8. Click "Reference variables from another service"
9. Select your API service to copy all variables
10. Click "Add References"
11. Go to the "Settings" tab
12. Under "Start Command", enter: `rq worker --with-scheduler`
13. Click "Deploy" to apply changes

### Run Database Migrations

1. In your project dashboard, click "New"
2. Select "GitHub Repo"
3. Select the same repository
4. Set the root directory to the project root (where alembic.ini is located)
5. Click "Deploy"
6. Wait for the initial deployment to complete
7. Go to the "Variables" tab
8. Click "Reference variables from another service"
9. Select your API service to copy all variables
10. Click "Add References"
11. Go to the "Settings" tab
12. Under "Start Command", enter: `alembic upgrade head`
13. Click "Deploy" to apply changes
14. Wait for the deployment to complete
15. Check the logs to ensure migrations ran successfully
16. Once migrations are complete, delete this service

### Get Your API URL

1. Go to your API service
2. Click on the "Settings" tab
3. Look for "Service Domain" - this is your API URL
4. Save this URL for your Vercel configuration

## 3. Vercel Setup

### Create a Vercel Account

1. Go to [Vercel](https://vercel.com/) and sign up or log in with GitHub

### Import Your Project

1. Click "Add New..." and select "Project"
2. Select your GitHub repository
3. If prompted, install the Vercel GitHub app

### Configure Project

1. Vercel will automatically detect Next.js
2. Under "Framework Preset", ensure "Next.js" is selected
3. Under "Root Directory", select "frontend"
4. Add the following environment variables:
   - `NEXT_PUBLIC_BACKEND_URL`: Your Railway API URL
   - `NEXTAUTH_SECRET`: Same value used in Railway
   - `NEXTAUTH_URL`: Your Vercel deployment URL (will be generated after deployment)
5. Click "Deploy"

### Update Environment Variables After Deployment

1. Once deployed, go to your project dashboard
2. Click on "Settings" tab
3. Click on "Environment Variables"
4. Update `NEXTAUTH_URL` with your actual Vercel deployment URL
5. Click "Save"
6. Go to the "Deployments" tab
7. Find your latest deployment
8. Click the three dots menu and select "Redeploy"

## 4. Custom Domain Setup (Optional)

### Configure Domain on Vercel

1. In your Vercel project, go to "Settings"
2. Click on "Domains"
3. Enter your domain name (e.g., "yourdomain.com")
4. Click "Add"
5. Follow the instructions to configure your DNS settings

### Configure API Subdomain on Railway

1. In your Railway project, click on your API service
2. Go to "Settings"
3. Under "Domains", click "Generate Domain"
4. Copy the generated domain
5. Create a CNAME record in your DNS settings:
   - Name/Host: "api" (this will create api.yourdomain.com)
   - Value/Target: Your Railway generated domain
   - TTL: 3600 (or "Automatic")

### Update Environment Variables

1. In your Vercel project, update `NEXT_PUBLIC_BACKEND_URL` to "https://api.yourdomain.com"
2. In your Railway project, update the CORS settings in main.py to include your domain

## Troubleshooting

### Railway Deployment Issues

- **Dockerfile Error**: Ensure the Dockerfile is correctly configured to find requirements.txt
  - Make sure you're setting the root directory to the project root, not the backend directory
  - Check that the "Service Path" is set to `/backend` in the service settings
- **Environment Variables**: Double-check all environment variables are set correctly
- **Database Connection**: Verify the Supabase connection string is correct

### Supabase Issues

- **Storage Permissions**: Ensure the storage bucket has the correct policies
- **Database Connection**: Check that the database password is correct in the connection string

### Vercel Deployment Issues

- **Build Errors**: Check the build logs for any errors
- **API Connection**: Ensure the `NEXT_PUBLIC_BACKEND_URL` is set correctly
- **Authentication**: Verify that `NEXTAUTH_SECRET` and `NEXTAUTH_URL` are set correctly

## Maintenance

### Database Backups

- Supabase provides automatic backups on the free tier
- Consider setting up additional backup solutions for production

### Monitoring

- Use Railway's built-in monitoring for backend services
- Use Vercel's analytics for frontend monitoring
- Consider setting up additional monitoring solutions for production

### Scaling

When you need to scale:

1. **Supabase**: Upgrade to the Pro plan for more storage and database capacity
2. **Railway**: Increase resources for your services
3. **Vercel**: The free tier should be sufficient for most use cases
