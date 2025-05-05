#!/usr/bin/env python3
"""
Check Live Railway Variables Script

This script checks the environment variables in the live Railway services
and compares them with the required variables.

Usage:
    python check_live_railway_vars.py
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

def check_railway_variables():
    """Check Railway environment variables."""
    print_section("Railway Environment Variables")
    
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
    
    # Get Railway services
    services = get_railway_services()
    
    if not services:
        print_error("No Railway services found.")
        return
    
    for service in services:
        service_id = service.get('id')
        service_name = service.get('name')
        
        print_info(f"Environment variables for service: {service_name}")
        
        # Get environment variables for the service
        variables = get_railway_variables(service_id)
        
        if not variables:
            print_error(f"No environment variables found for service: {service_name}")
            continue
        
        # Check if required variables are present
        missing_vars = []
        for var in key_vars:
            if var in variables:
                # Mask sensitive values
                if any(sensitive in var.lower() for sensitive in ['key', 'secret', 'password', 'token', 'url']):
                    print_success(f"  {var} = ****")
                else:
                    print_success(f"  {var} = {variables[var]}")
            else:
                print_error(f"  {var} is missing")
                missing_vars.append(var)
        
        if missing_vars:
            print_warning(f"Service {service_name} is missing {len(missing_vars)} required variables:")
            for var in missing_vars:
                print_warning(f"  - {var}")
        else:
            print_success(f"Service {service_name} has all required variables.")

def check_vercel_variables():
    """Check Vercel environment variables."""
    print_section("Vercel Environment Variables")
    
    try:
        # Check if Vercel CLI is installed and logged in
        vercel_whoami = run_command("vercel whoami")
        if not vercel_whoami:
            print_warning("Vercel CLI not installed or not logged in. Skipping Vercel checks.")
            return
        
        # Get Vercel projects
        projects = run_command("vercel project ls --json")
        if not projects:
            print_error("No Vercel projects found.")
            return
        
        projects_json = json.loads(projects)
        
        for project in projects_json:
            project_id = project.get('id')
            project_name = project.get('name')
            
            print_info(f"Environment variables for project: {project_name}")
            
            # Get environment variables for the project
            env_vars = run_command(f"vercel env ls {project_id} --json")
            if not env_vars:
                print_error(f"No environment variables found for project: {project_name}")
                continue
            
            env_vars_json = json.loads(env_vars)
            
            # Key variables that should be in Vercel
            key_vars = [
                "NEXT_PUBLIC_BACKEND_URL",
                "NEXT_PUBLIC_UPLOADS_URL",
                "NEXTAUTH_SECRET",
                "NEXT_PUBLIC_SUPABASE_URL",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY"
            ]
            
            # Check if required variables are present
            missing_vars = []
            for var in key_vars:
                found = False
                for env_var in env_vars_json:
                    if env_var.get('key') == var:
                        found = True
                        # Mask sensitive values
                        if any(sensitive in var.lower() for sensitive in ['key', 'secret', 'password', 'token', 'url']):
                            print_success(f"  {var} = ****")
                        else:
                            print_success(f"  {var} = {env_var.get('value')}")
                        break
                
                if not found:
                    print_error(f"  {var} is missing")
                    missing_vars.append(var)
            
            if missing_vars:
                print_warning(f"Project {project_name} is missing {len(missing_vars)} required variables:")
                for var in missing_vars:
                    print_warning(f"  - {var}")
            else:
                print_success(f"Project {project_name} has all required variables.")
    except Exception as e:
        print_error(f"Error checking Vercel variables: {str(e)}")

def main():
    """Main function."""
    print_header("Check Live Railway and Vercel Variables")
    
    print_info("This script checks the environment variables in the live Railway services")
    print_info("and Vercel projects and compares them with the required variables.")
    print_info("")
    print_info("Make sure you have the Railway CLI and Vercel CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    check_railway_variables()
    check_vercel_variables()
    
    print_header("Check Complete")

if __name__ == "__main__":
    main()
