#!/bin/bash
# Fix Deployment Script
# This script fixes the deployment issues by:
# 1. Synchronizing environment variables across platforms
# 2. Redeploying Railway services

# Print colored output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
print_header() {
  echo -e "\n${BLUE}================================================================================${NC}"
  echo -e "${BLUE}                            $1                            ${NC}"
  echo -e "${BLUE}================================================================================${NC}\n"
}

# Print section
print_section() {
  echo -e "\n${YELLOW}--------------------------------------------------------------------------------${NC}"
  echo -e "${YELLOW}                            $1                            ${NC}"
  echo -e "${YELLOW}--------------------------------------------------------------------------------${NC}\n"
}

# Print success message
print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

# Print error message
print_error() {
  echo -e "${RED}❌ $1${NC}"
}

# Print info message
print_info() {
  echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if Railway CLI is installed
check_railway_cli() {
  print_section "Checking Railway CLI"
  
  if ! command -v railway &> /dev/null; then
    print_error "Railway CLI is not installed."
    print_info "Installing Railway CLI..."
    
    # Install Railway CLI
    npm install -g @railway/cli
    
    if [ $? -ne 0 ]; then
      print_error "Failed to install Railway CLI. Please install it manually."
      exit 1
    else
      print_success "Railway CLI installed successfully."
    fi
  else
    print_success "Railway CLI is already installed."
  fi
  
  # Check if logged in
  railway whoami &> /dev/null
  
  if [ $? -ne 0 ]; then
    print_error "Not logged in to Railway."
    print_info "Please log in to Railway:"
    railway login
    
    if [ $? -ne 0 ]; then
      print_error "Failed to log in to Railway. Please log in manually."
      exit 1
    else
      print_success "Logged in to Railway successfully."
    fi
  else
    print_success "Already logged in to Railway."
  fi
}

# Check if Vercel CLI is installed
check_vercel_cli() {
  print_section "Checking Vercel CLI"
  
  if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed."
    print_info "Installing Vercel CLI..."
    
    # Install Vercel CLI
    npm install -g vercel
    
    if [ $? -ne 0 ]; then
      print_error "Failed to install Vercel CLI. Please install it manually."
      exit 1
    else
      print_success "Vercel CLI installed successfully."
    fi
  else
    print_success "Vercel CLI is already installed."
  fi
  
  # Check if logged in
  vercel whoami &> /dev/null
  
  if [ $? -ne 0 ]; then
    print_error "Not logged in to Vercel."
    print_info "Please log in to Vercel:"
    vercel login
    
    if [ $? -ne 0 ]; then
      print_error "Failed to log in to Vercel. Please log in manually."
      exit 1
    else
      print_success "Logged in to Vercel successfully."
    fi
  else
    print_success "Already logged in to Vercel."
  fi
}

# Synchronize environment variables
sync_env_vars() {
  print_section "Synchronizing Environment Variables"
  
  print_info "Running environment variables synchronization script..."
  python sync_environment_variables.py
  
  if [ $? -ne 0 ]; then
    print_error "Failed to synchronize environment variables."
    exit 1
  else
    print_success "Environment variables synchronized successfully."
  fi
}

# Redeploy Railway services
redeploy_railway_services() {
  print_section "Redeploying Railway Services"
  
  # Get Railway services
  print_info "Getting Railway services..."
  services=$(railway service list --json)
  
  if [ $? -ne 0 ]; then
    print_error "Failed to get Railway services."
    exit 1
  fi
  
  # Parse services
  echo "$services" | jq -c '.[]' | while read -r service; do
    service_id=$(echo "$service" | jq -r '.id')
    service_name=$(echo "$service" | jq -r '.name')
    
    print_info "Redeploying service: $service_name"
    railway up --service "$service_id"
    
    if [ $? -ne 0 ]; then
      print_error "Failed to redeploy service: $service_name"
    else
      print_success "Service redeployed successfully: $service_name"
    fi
  done
}

# Main function
main() {
  print_header "Fix Deployment Script"
  
  print_info "This script will fix the deployment issues by:"
  print_info "1. Synchronizing environment variables across platforms"
  print_info "2. Redeploying Railway services"
  print_info ""
  print_info "Press Enter to continue or Ctrl+C to exit."
  read
  
  # Check if required tools are installed
  check_railway_cli
  check_vercel_cli
  
  # Synchronize environment variables
  sync_env_vars
  
  # Redeploy Railway services
  redeploy_railway_services
  
  print_header "Deployment Fix Complete"
  print_info "The deployment issues should now be fixed."
  print_info "Please check the Railway and Vercel dashboards to verify the deployments."
}

# Run main function
main
