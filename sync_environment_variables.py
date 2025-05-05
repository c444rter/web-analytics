#!/usr/bin/env python3
"""
Synchronize Environment Variables Across Platforms

This script synchronizes environment variables across Supabase, Vercel, and Railway
to ensure consistent configuration.

Usage:
    python sync_environment_variables.py
"""

import os
import sys
import json
import subprocess
import requests
from urllib.parse import urlparse
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
                            
                            # Only add if not already in env_vars
                            if key not in env_vars:
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
        output = run_command(f"railway variables list --service {service_id} --json")
        if output:
            variables = json.loads(output)
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

def get_vercel_projects():
    """Get list of Vercel projects."""
    try:
        output = run_command("vercel project ls --json")
        if output:
            projects = json.loads(output)
            return projects
        return []
    except Exception as e:
        print_error(f"Error getting Vercel projects: {str(e)}")
        return []

def get_vercel_env_vars(project_id):
    """Get Vercel environment variables for a project."""
    try:
        output = run_command(f"vercel env ls {project_id} --json")
        if output:
            env_vars = json.loads(output)
            return env_vars
        return {}
    except Exception as e:
        print_error(f"Error getting Vercel environment variables: {str(e)}")
        return {}

def update_vercel_env_vars(project_id, env_vars):
    """Update Vercel environment variables for a project."""
    for key, value in env_vars.items():
        print_info(f"Setting {key} for project {project_id}")
        # Create a temporary file for the environment variable
        with open("temp_env_var.txt", "w") as f:
            f.write(value)
        
        command = f'vercel env add {key} production < temp_env_var.txt --project {project_id}'
        result = run_command(command)
        
        # Clean up
        if os.path.exists("temp_env_var.txt"):
            os.remove("temp_env_var.txt")
            
        if result is not None:
            print_success(f"Successfully set {key}")
        else:
            print_error(f"Failed to set {key}")

def get_supabase_variables():
    """Get Supabase variables from local files."""
    supabase_vars = {}
    env_files = [
        ".env.vercel.production",
        ".env.local",
        "backend/.env.local",
        ".env"
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            
                            if key.startswith("SUPABASE_"):
                                supabase_vars[key] = value
                        except ValueError:
                            continue
    
    return supabase_vars

def sync_environment_variables():
    """Synchronize environment variables across platforms."""
    # Get all environment variables from local files
    all_env_vars = get_env_vars_from_files()
    
    if not all_env_vars:
        print_error("No environment variables found in local files.")
        return
    
    print_section("Found Environment Variables")
    print_info(f"Found {len(all_env_vars)} environment variables in local files.")
    
    # Categorize variables by platform
    railway_vars = {}
    vercel_vars = {}
    
    # Variables that should be in Railway
    railway_keys = [
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
    
    # Variables that should be in Vercel
    vercel_keys = [
        "NEXT_PUBLIC_BACKEND_URL",
        "NEXT_PUBLIC_UPLOADS_URL",
        "NEXTAUTH_SECRET",
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
    
    # Populate platform-specific variables
    for key, value in all_env_vars.items():
        if key in railway_keys:
            railway_vars[key] = value
        if key in vercel_keys:
            vercel_vars[key] = value
    
    # Ensure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set in Vercel
    if "SUPABASE_URL" in all_env_vars and "NEXT_PUBLIC_SUPABASE_URL" not in vercel_vars:
        vercel_vars["NEXT_PUBLIC_SUPABASE_URL"] = all_env_vars["SUPABASE_URL"]
    
    if "SUPABASE_KEY" in all_env_vars and "NEXT_PUBLIC_SUPABASE_ANON_KEY" not in vercel_vars:
        vercel_vars["NEXT_PUBLIC_SUPABASE_ANON_KEY"] = all_env_vars["SUPABASE_KEY"]
    
    # Get Railway services
    print_section("Railway Services")
    services = get_railway_services()
    
    if not services:
        print_error("No Railway services found.")
    else:
        for i, service in enumerate(services):
            print_info(f"{i+1}. {service.get('name')} ({service.get('id')})")
        
        # Update Railway services
        print_section("Updating Railway Environment Variables")
        
        for service in services:
            print_info(f"Updating service: {service.get('name')}")
            
            # Get existing variables
            existing_vars = get_railway_variables(service.get('id'))
            
            # Determine which variables need to be updated
            vars_to_update = {}
            for key, value in railway_vars.items():
                if key not in existing_vars or existing_vars[key] != value:
                    vars_to_update[key] = value
            
            if vars_to_update:
                print_info(f"Updating {len(vars_to_update)} variables for {service.get('name')}")
                update_railway_env_vars(service.get('id'), vars_to_update)
            else:
                print_success(f"All variables are already up to date for {service.get('name')}")
    
    # Get Vercel projects
    print_section("Vercel Projects")
    
    try:
        # Check if Vercel CLI is installed and logged in
        vercel_whoami = run_command("vercel whoami")
        if not vercel_whoami:
            print_warning("Vercel CLI not installed or not logged in. Skipping Vercel updates.")
        else:
            projects = get_vercel_projects()
            
            if not projects:
                print_error("No Vercel projects found.")
            else:
                for i, project in enumerate(projects):
                    print_info(f"{i+1}. {project.get('name')} ({project.get('id')})")
                
                # Update Vercel projects
                print_section("Updating Vercel Environment Variables")
                
                for project in projects:
                    print_info(f"Updating project: {project.get('name')}")
                    
                    # Get existing variables
                    existing_vars = get_vercel_env_vars(project.get('id'))
                    
                    # Determine which variables need to be updated
                    vars_to_update = {}
                    for key, value in vercel_vars.items():
                        if key not in existing_vars or existing_vars[key] != value:
                            vars_to_update[key] = value
                    
                    if vars_to_update:
                        print_info(f"Updating {len(vars_to_update)} variables for {project.get('name')}")
                        update_vercel_env_vars(project.get('id'), vars_to_update)
                    else:
                        print_success(f"All variables are already up to date for {project.get('name')}")
    except Exception as e:
        print_error(f"Error updating Vercel projects: {str(e)}")
    
    print_section("Environment Variables Synchronization Complete")
    print_info("Please redeploy your services for the changes to take effect.")

def main():
    """Main function."""
    print_header("Synchronize Environment Variables Across Platforms")
    
    print_info("This script will synchronize environment variables across Supabase, Vercel, and Railway.")
    print_info("Make sure you have the Railway CLI and Vercel CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    sync_environment_variables()

if __name__ == "__main__":
    main()
