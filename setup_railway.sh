#!/bin/bash

# Railway CLI Setup and Usage Script
# This script helps you set up and use the Railway CLI for your web-analytics project

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Railway CLI Setup and Usage Script ===${NC}"
echo -e "${BLUE}This script will help you set up and use the Railway CLI for your web-analytics project${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 14+ before continuing.${NC}"
    echo "Visit https://nodejs.org/ to download and install Node.js"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm before continuing.${NC}"
    exit 1
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI is not installed. Installing now...${NC}"
    npm install -g @railway/cli
    
    # Check if installation was successful
    if ! command -v railway &> /dev/null; then
        echo -e "${RED}Failed to install Railway CLI. Please install it manually:${NC}"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    echo -e "${GREEN}Railway CLI installed successfully!${NC}"
else
    echo -e "${GREEN}Railway CLI is already installed.${NC}"
fi

# Display Railway CLI version
RAILWAY_VERSION=$(railway --version)
echo -e "${GREEN}Railway CLI version: ${RAILWAY_VERSION}${NC}"
echo ""

# Login to Railway
echo -e "${YELLOW}Logging in to Railway...${NC}"
echo "This will open a browser window where you can authenticate with your Railway account."
railway login
echo ""

# Check if login was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to log in to Railway. Please try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully logged in to Railway!${NC}"
echo ""

# Link to Railway project
echo -e "${YELLOW}Linking to Railway project...${NC}"
echo "Select your project from the list that appears."
railway link
echo ""

# Check if link was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to link to Railway project. Please try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Successfully linked to Railway project!${NC}"
echo ""

# Set environment variables
echo -e "${YELLOW}Do you want to set environment variables for your project? (y/n)${NC}"
read -r set_vars

if [[ $set_vars == "y" || $set_vars == "Y" ]]; then
    echo -e "${YELLOW}Setting environment variables...${NC}"
    
    # Get Supabase database URL
    echo -e "${YELLOW}Enter your Supabase database URL (postgresql://postgres:[YOUR-PASSWORD]@db.tipdainlasfkkgwxoexm.pooler.supabase.co:5432/postgres):${NC}"
    read -r database_url
    railway vars set DATABASE_URL="$database_url"
    
    # Get Supabase URL
    echo -e "${YELLOW}Enter your Supabase URL (https://tipdainlasfkkgwxoexm.supabase.co):${NC}"
    read -r supabase_url
    railway vars set SUPABASE_URL="$supabase_url"
    
    # Get Supabase key
    echo -e "${YELLOW}Enter your Supabase anon key:${NC}"
    read -r supabase_key
    railway vars set SUPABASE_KEY="$supabase_key"
    
    # Set bucket name
    railway vars set BUCKET_NAME="uploads"
    
    # Get secret key
    echo -e "${YELLOW}Enter your secret key:${NC}"
    read -r secret_key
    railway vars set SECRET_KEY="$secret_key"
    
    # Get NextAuth secret
    echo -e "${YELLOW}Enter your NextAuth secret:${NC}"
    read -r nextauth_secret
    railway vars set NEXTAUTH_SECRET="$nextauth_secret"
    
    # Set Redis DB
    railway vars set REDIS_DB="0"
    
    echo -e "${GREEN}Environment variables set successfully!${NC}"
    echo ""
fi

# Deploy application
echo -e "${YELLOW}Do you want to deploy your application? (y/n)${NC}"
read -r deploy_app

if [[ $deploy_app == "y" || $deploy_app == "Y" ]]; then
    echo -e "${YELLOW}Deploying application...${NC}"
    railway up
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to deploy application. Please check the logs and try again.${NC}"
    else
        echo -e "${GREEN}Application deployed successfully!${NC}"
    fi
    echo ""
fi

# Run migrations
echo -e "${YELLOW}Do you want to run migrations? (y/n)${NC}"
read -r run_migrations

if [[ $run_migrations == "y" || $run_migrations == "Y" ]]; then
    echo -e "${YELLOW}Running migrations...${NC}"
    railway run alembic upgrade head
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to run migrations. Please check the logs and try again.${NC}"
    else
        echo -e "${GREEN}Migrations ran successfully!${NC}"
    fi
    echo ""
fi

# Migrate data
echo -e "${YELLOW}Do you want to migrate data from your local database to Supabase? (y/n)${NC}"
read -r migrate_data

if [[ $migrate_data == "y" || $migrate_data == "Y" ]]; then
    echo -e "${YELLOW}Migrating data...${NC}"
    
    # Check if migrate_to_supabase.py exists
    if [ ! -f "migrate_to_supabase.py" ]; then
        echo -e "${RED}migrate_to_supabase.py not found. Please make sure the file exists.${NC}"
    else
        # Update LOCAL_DB_URL in migrate_to_supabase.py
        echo -e "${YELLOW}Enter your local database URL (postgresql://postgres:postgres@localhost:5432/my_davids):${NC}"
        read -r local_db_url
        
        # Use sed to replace the LOCAL_DB_URL line in migrate_to_supabase.py
        sed -i '' "s|LOCAL_DB_URL = .*|LOCAL_DB_URL = \"$local_db_url\"|" migrate_to_supabase.py
        
        # Run the migration script
        railway run python migrate_to_supabase.py
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to migrate data. Please check the logs and try again.${NC}"
        else
            echo -e "${GREEN}Data migrated successfully!${NC}"
        fi
    fi
    echo ""
fi

# Open application
echo -e "${YELLOW}Do you want to open your application in the browser? (y/n)${NC}"
read -r open_app

if [[ $open_app == "y" || $open_app == "Y" ]]; then
    echo -e "${YELLOW}Opening application...${NC}"
    railway open
    echo ""
fi

echo -e "${GREEN}Railway CLI setup and usage complete!${NC}"
echo -e "${BLUE}For more information, see RAILWAY_CLI_GUIDE.md${NC}"
