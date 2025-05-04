#!/bin/bash
# Reset Exposed Secrets Script
# This script helps reset exposed secrets and update them in deployment environments

# Set the script to exit on error
set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display section header
section() {
  echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

# Function to display success message
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to display warning message
warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to display error message
error() {
  echo -e "${RED}✗ $1${NC}"
}

# Function to display info message
info() {
  echo -e "${BLUE}ℹ $1${NC}"
}

# Function to prompt for confirmation
confirm() {
  read -p "$1 (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    return 1
  fi
  return 0
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Display welcome message
section "EXPOSED SECRETS RESET TOOL"
echo "This script will help you reset exposed secrets and update them in your deployment environments."
echo "The following secrets may have been exposed:"
echo "  - Supabase anon key"
echo "  - Supabase service role key"
echo
warning "IMPORTANT: This process will invalidate your current Supabase keys."
echo "Make sure you have access to your Supabase dashboard and deployment environments."
echo

# Confirm before proceeding
if ! confirm "Do you want to proceed with resetting your exposed secrets?"; then
  echo "Exiting without making any changes."
  exit 0
fi

# Check for required tools
section "CHECKING REQUIRED TOOLS"

# Check for curl
if ! command_exists curl; then
  error "curl is not installed. Please install curl and try again."
  exit 1
else
  success "curl is installed."
fi

# Check for jq
if ! command_exists jq; then
  warning "jq is not installed. It's recommended for parsing JSON responses."
  if confirm "Would you like to install jq now?"; then
    if command_exists apt-get; then
      sudo apt-get update && sudo apt-get install -y jq
    elif command_exists brew; then
      brew install jq
    else
      error "Could not determine package manager. Please install jq manually."
      exit 1
    fi
  fi
else
  success "jq is installed."
fi

# Step 1: Reset Supabase API Keys
section "STEP 1: RESET SUPABASE API KEYS"
echo "You need to reset your Supabase API keys from the Supabase dashboard."
echo "Follow these steps:"
echo "1. Log in to your Supabase dashboard at https://app.supabase.com"
echo "2. Select your project"
echo "3. Go to Project Settings → API"
echo "4. Click on 'Rotate API keys' button"
echo "5. Confirm the rotation"
echo "6. Copy the new anon key and service role key"
echo

# Prompt for new keys
echo "Enter your new Supabase anon key:"
read -r NEW_SUPABASE_KEY
echo "Enter your new Supabase service role key:"
read -r NEW_SUPABASE_SERVICE_ROLE_KEY

if [[ -z "$NEW_SUPABASE_KEY" || -z "$NEW_SUPABASE_SERVICE_ROLE_KEY" ]]; then
  error "Both keys are required. Please try again."
  exit 1
fi

success "New Supabase keys received."

# Step 2: Update Railway Environment Variables
section "STEP 2: UPDATE RAILWAY ENVIRONMENT VARIABLES"
echo "You need to update your Railway environment variables with the new Supabase keys."
echo "Follow these steps:"
echo "1. Log in to your Railway dashboard at https://railway.app"
echo "2. Select your project"
echo "3. Go to the 'Variables' tab"
echo "4. Update the following variables:"
echo "   - SUPABASE_KEY: $NEW_SUPABASE_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY: $NEW_SUPABASE_SERVICE_ROLE_KEY"
echo "5. Click 'Save' to apply the changes"
echo

if confirm "Have you updated the Railway environment variables?"; then
  success "Railway environment variables updated."
else
  warning "Please update the Railway environment variables before continuing."
  if ! confirm "Continue anyway?"; then
    echo "Exiting. Please complete this step and run the script again."
    exit 0
  fi
fi

# Step 3: Update Vercel Environment Variables
section "STEP 3: UPDATE VERCEL ENVIRONMENT VARIABLES"
echo "You need to update your Vercel environment variables with the new Supabase keys."
echo "Follow these steps:"
echo "1. Log in to your Vercel dashboard at https://vercel.com"
echo "2. Select your project"
echo "3. Go to 'Settings' → 'Environment Variables'"
echo "4. Update the following variables:"
echo "   - NEXT_PUBLIC_SUPABASE_URL: (should remain the same)"
echo "   - NEXT_PUBLIC_SUPABASE_ANON_KEY: $NEW_SUPABASE_KEY"
echo "5. Click 'Save' to apply the changes"
echo "6. Redeploy your application"
echo

if confirm "Have you updated the Vercel environment variables?"; then
  success "Vercel environment variables updated."
else
  warning "Please update the Vercel environment variables before continuing."
  if ! confirm "Continue anyway?"; then
    echo "Exiting. Please complete this step and run the script again."
    exit 0
  fi
fi

# Step 4: Update GitHub Secrets
section "STEP 4: UPDATE GITHUB SECRETS"
echo "You need to update your GitHub repository secrets with the new Supabase keys."
echo "Follow these steps:"
echo "1. Go to your GitHub repository"
echo "2. Click on 'Settings' tab"
echo "3. In the left sidebar, click on 'Secrets and variables' → 'Actions'"
echo "4. Update the following secrets:"
echo "   - SUPABASE_KEY: $NEW_SUPABASE_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY: $NEW_SUPABASE_SERVICE_ROLE_KEY"
echo "5. Click 'Update secret' for each"
echo

if confirm "Have you updated the GitHub secrets?"; then
  success "GitHub secrets updated."
else
  warning "Please update the GitHub secrets before continuing."
  if ! confirm "Continue anyway?"; then
    echo "Exiting. Please complete this step and run the script again."
    exit 0
  fi
fi

# Step 5: Update Local Environment Variables
section "STEP 5: UPDATE LOCAL ENVIRONMENT VARIABLES"
echo "You need to update your local environment variables with the new Supabase keys."
echo "The following files may contain the old keys:"
echo "  - .env"
echo "  - .env.local"
echo "  - backend/.env"
echo "  - backend/.env.local"
echo "  - frontend/.env"
echo "  - frontend/.env.local"
echo

# Update .env files
for env_file in .env .env.local backend/.env backend/.env.local frontend/.env frontend/.env.local; do
  if [[ -f "$env_file" ]]; then
    info "Checking $env_file..."
    
    # Create a backup
    cp "$env_file" "${env_file}.bak"
    success "Created backup: ${env_file}.bak"
    
    # Update the keys
    if grep -q "SUPABASE_KEY" "$env_file"; then
      sed -i.tmp "s|SUPABASE_KEY=.*|SUPABASE_KEY=$NEW_SUPABASE_KEY|g" "$env_file"
      success "Updated SUPABASE_KEY in $env_file"
    fi
    
    if grep -q "SUPABASE_SERVICE_ROLE_KEY" "$env_file"; then
      sed -i.tmp "s|SUPABASE_SERVICE_ROLE_KEY=.*|SUPABASE_SERVICE_ROLE_KEY=$NEW_SUPABASE_SERVICE_ROLE_KEY|g" "$env_file"
      success "Updated SUPABASE_SERVICE_ROLE_KEY in $env_file"
    fi
    
    if grep -q "NEXT_PUBLIC_SUPABASE_ANON_KEY" "$env_file"; then
      sed -i.tmp "s|NEXT_PUBLIC_SUPABASE_ANON_KEY=.*|NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEW_SUPABASE_KEY|g" "$env_file"
      success "Updated NEXT_PUBLIC_SUPABASE_ANON_KEY in $env_file"
    fi
    
    # Remove temporary files
    rm -f "${env_file}.tmp"
  fi
done

# Step 6: Verify the Changes
section "STEP 6: VERIFY THE CHANGES"
echo "Let's verify that the changes were applied correctly."
echo

# Check if the keys were updated in the local environment
for env_file in .env .env.local backend/.env backend/.env.local frontend/.env frontend/.env.local; do
  if [[ -f "$env_file" ]]; then
    if grep -q "$NEW_SUPABASE_KEY" "$env_file" || grep -q "$NEW_SUPABASE_SERVICE_ROLE_KEY" "$env_file"; then
      success "Verified that $env_file contains the new keys."
    else
      warning "$env_file may not have been updated correctly. Please check manually."
    fi
  fi
done

# Final steps
section "NEXT STEPS"
echo "You have successfully reset your exposed Supabase keys and updated them in your deployment environments."
echo "Here are some additional steps you should take:"
echo
echo "1. Commit the changes to your local environment files:"
echo "   git add .env.local backend/.env.local frontend/.env.local"
echo "   git commit -m \"Update Supabase keys\""
echo
echo "2. Push the changes to GitHub:"
echo "   git push origin main"
echo
echo "3. Monitor your deployments to ensure everything is working correctly."
echo
echo "4. Consider implementing a secrets management solution to prevent future exposures."
echo

success "Secret rotation complete!"
