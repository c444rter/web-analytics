#!/usr/bin/env python3
"""
Fix Backend Deployment Script

This script fixes the backend deployment issues by:
1. Ensuring all required environment variables are set in Railway
2. Redeploying the backend service

Usage:
    python fix_backend_deployment.py
"""

import os
import sys
import json
import subprocess
import time

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def print_section(text):
    """Print a section header."""
    print("\n" + "-" * 80)
    print(f" {text} ".center(80, "-"))
    print("-" * 80 + "\n")

def print_success(text):
    """Print a success message."""
    print(f"✅ {text}")

def print_error(text):
    """Print an error message."""
    print(f"❌ {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"⚠️ {text}")

def print_info(text):
    """Print an info message."""
    print(f"ℹ️ {text}")

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def get_env_vars_from_files():
    """Get environment variables from local files."""
    env_vars = {}
    env_files = [
        ".env.vercel.production",
        ".env.local",
        "backend/.env.local",
        ".env"
    ]
    
    # Key variables that should be in Railway
    key_vars = [
        "DATABASE_URL",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SECRET_KEY",
        "NEXTAUTH_SECRET",
        "REDIS_PUBLIC_URL",
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD",
        "REDIS_USER",
        "BUCKET_NAME"
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print_info(f"Reading environment variables from {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            
                            if key in key_vars and key not in env_vars:
                                env_vars[key] = value
                        except ValueError:
                            continue
    
    return env_vars

def get_railway_services():
    """Get list of Railway services."""
    try:
        output = run_command("railway service list --json")
        if output:
            services = json.loads(output)
            return services
        return []
    except Exception as e:
        print_error(f"Error getting Railway services: {str(e)}")
        return []

def get_railway_variables(service_id):
    """Get Railway environment variables for a service."""
    try:
        output = run_command(f"railway variables get --service {service_id}")
        if output:
            variables = {}
            for line in output.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    variables[key.strip()] = value.strip()
            return variables
        return {}
    except Exception as e:
        print_error(f"Error getting Railway variables: {str(e)}")
        return {}

def update_railway_env_vars(service_id, env_vars):
    """Update Railway environment variables for a service."""
    for key, value in env_vars.items():
        print_info(f"Setting {key} for service {service_id}")
        command = f'railway variables set {key}="{value}" --service {service_id}'
        result = run_command(command)
        if result is not None:
            print_success(f"Successfully set {key}")
        else:
            print_error(f"Failed to set {key}")

def redeploy_railway_service(service_id, service_name):
    """Redeploy a Railway service."""
    print_info(f"Redeploying service: {service_name}")
    result = run_command(f"railway up --service {service_id} --detach")
    if result is not None:
        print_success(f"Successfully redeployed service: {service_name}")
    else:
        print_error(f"Failed to redeploy service: {service_name}")

def check_railway_logs(service_id, service_name):
    """Check Railway logs for a service."""
    print_info(f"Checking logs for service: {service_name}")
    logs = run_command(f"railway logs --service {service_id} --limit 20")
    if logs:
        print_info("Latest logs:")
        print(logs)
    else:
        print_error(f"Failed to get logs for service: {service_name}")

def fix_backend_deployment():
    """Fix backend deployment issues."""
    # Get environment variables from local files
    env_vars = get_env_vars_from_files()
    
    if not env_vars:
        print_error("No environment variables found in local files.")
        return
    
    print_section("Found Environment Variables")
    print_info(f"Found {len(env_vars)} environment variables in local files.")
    
    # Get Railway services
    print_section("Railway Services")
    services = get_railway_services()
    
    if not services:
        print_error("No Railway services found.")
        return
    
    for i, service in enumerate(services):
        print_info(f"{i+1}. {service.get('name')} ({service.get('id')})")
    
    # Ask which services to update
    print_info("\nWhich services do you want to update? (Enter comma-separated numbers, or 'all')")
    choice = input().strip().lower()
    
    selected_services = []
    if choice == 'all':
        selected_services = services
    else:
        try:
            indices = [int(idx.strip()) - 1 for idx in choice.split(',')]
            selected_services = [services[idx] for idx in indices if 0 <= idx < len(services)]
        except (ValueError, IndexError):
            print_error("Invalid selection.")
            return
    
    if not selected_services:
        print_error("No services selected.")
        return
    
    # Update environment variables for selected services
    print_section("Updating Environment Variables")
    
    for service in selected_services:
        service_id = service.get('id')
        service_name = service.get('name')
        
        print_info(f"Updating service: {service_name}")
        
        # Get existing variables
        existing_vars = get_railway_variables(service_id)
        
        # Determine which variables need to be updated
        vars_to_update = {}
        for key, value in env_vars.items():
            if key not in existing_vars or existing_vars[key] != value:
                vars_to_update[key] = value
        
        if vars_to_update:
            print_info(f"Updating {len(vars_to_update)} variables for {service_name}")
            update_railway_env_vars(service_id, vars_to_update)
        else:
            print_success(f"All variables are already up to date for {service_name}")
    
    # Redeploy selected services
    print_section("Redeploying Services")
    
    for service in selected_services:
        service_id = service.get('id')
        service_name = service.get('name')
        
        redeploy_railway_service(service_id, service_name)
    
    # Wait for services to start
    print_section("Waiting for Services to Start")
    print_info("Waiting 30 seconds for services to start...")
    time.sleep(30)
    
    # Check logs for selected services
    print_section("Checking Service Logs")
    
    for service in selected_services:
        service_id = service.get('id')
        service_name = service.get('name')
        
        check_railway_logs(service_id, service_name)

def main():
    """Main function."""
    print_header("Fix Backend Deployment")
    
    print_info("This script will fix the backend deployment issues by:")
    print_info("1. Ensuring all required environment variables are set in Railway")
    print_info("2. Redeploying the backend service")
    print_info("")
    print_info("Make sure you have the Railway CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    fix_backend_deployment()
    
    print_header("Backend Deployment Fix Complete")
    print_info("The backend deployment issues should now be fixed.")
    print_info("Please check the Railway dashboard to verify the deployment.")

if __name__ == "__main__":
    main()
