#!/usr/bin/env python3
"""
Update Railway Environment Variables Script

This script updates the Railway environment variables to ensure they include
the necessary database and Supabase configuration.

Usage:
    python update_railway_env.py
"""

import os
import sys
import subprocess
import json

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
    
    key_vars = [
        "DATABASE_URL",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SECRET_KEY",
        "NEXTAUTH_SECRET",
        "REDIS_PUBLIC_URL",
        "NEXT_PUBLIC_BACKEND_URL",
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

def main():
    """Main function."""
    print_header("Update Railway Environment Variables")
    
    print_info("This script will update the Railway environment variables to ensure they include")
    print_info("the necessary database and Supabase configuration.")
    print_info("Make sure you have the Railway CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    # Get environment variables from local files
    env_vars = get_env_vars_from_files()
    
    if not env_vars:
        print_error("No environment variables found in local files.")
        return
    
    print_section("Found Environment Variables")
    for key in sorted(env_vars.keys()):
        if "KEY" in key or "SECRET" in key or "PASSWORD" in key or "URL" in key:
            print_info(f"{key}: {'*' * 10}")
        else:
            print_info(f"{key}: {env_vars[key]}")
    
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
        print_info(f"Updating service: {service.get('name')}")
        update_railway_env_vars(service.get('id'), env_vars)
    
    print_header("Update Complete")
    print_info("Please redeploy your services for the changes to take effect.")

if __name__ == "__main__":
    main()
