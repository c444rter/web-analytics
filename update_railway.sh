#!/bin/bash
# This script updates the Railway environment variables

# Escape the @ symbol in the database URL
DATABASE_URL="postgresql://postgres.tipdainlasfkkgwxoexm:Gunners4ever2804!@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
SUPABASE_URL="https://tipdainlasfkkgwxoexm.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpcGRhaW5sYXNma2tnd3hvZXhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxMjMwMzAsImV4cCI6MjA2MTY5OTAzMH0.QMDgHwCJLrQuE8JvCEUHytRutsvwr509kS2EEWkPA8k"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpcGRhaW5sYXNma2tnd3hvZXhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjM4MjAwOCwiZXhwIjoyMDYxOTU4MDA4fQ.954IJLfK90WsrJZyhGDEaRB0YaHJkGOP-oN19cB0S1U"
SECRET_KEY="Gunners4ever032804!"
NEXTAUTH_SECRET="Gunners4ever032804!"
BUCKET_NAME="uploads"

# Update Railway environment variables
echo "Updating DATABASE_URL..."
railway variables --set "DATABASE_URL=$DATABASE_URL"

echo "Updating SUPABASE_URL..."
railway variables --set "SUPABASE_URL=$SUPABASE_URL"

echo "Updating SUPABASE_KEY..."
railway variables --set "SUPABASE_KEY=$SUPABASE_KEY"

echo "Updating SUPABASE_SERVICE_ROLE_KEY..."
railway variables --set "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"

echo "Updating SECRET_KEY..."
railway variables --set "SECRET_KEY=$SECRET_KEY"

echo "Updating NEXTAUTH_SECRET..."
railway variables --set "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"

echo "Updating BUCKET_NAME..."
railway variables --set "BUCKET_NAME=$BUCKET_NAME"

echo "Environment variables updated successfully!"
