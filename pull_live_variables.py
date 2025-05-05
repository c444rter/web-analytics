#!/usr/bin/env python3
"""
Pull Live Variables Script

This script pulls environment variables from live Railway and Vercel services
and updates the local environment files.

Usage:
    python pull_live_variables.py
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

def get_vercel_variables(project_id):
    """Get Vercel environment variables for a project."""
    try:
        output = run_command(f"vercel env ls {project_id} --json")
        if output:
            env_vars_json = json.loads(output)
            variables = {}
            for env_var in env_vars_json:
                if env_var.get('target') == 'production':
                    variables[env_var.get('key')] = env_var.get('value')
            return variables
        return {}
    except Exception as e:
        print_error(f"Error getting Vercel variables: {str(e)}")
        return {}

def update_env_file(file_path, variables):
    """Update an environment file with new variables."""
    if not os.path.exists(file_path):
        print_warning(f"File not found: {file_path}")
        # Create the file
        with open(file_path, 'w') as f:
            f.write("# Environment variables\n")
    
    # Read the current file
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Parse the current variables
    current_vars = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            try:
                key, value = line.split('=', 1)
                current_vars[key.strip()] = value.strip()
            except ValueError:
                pass
    
    # Update with new variables
    for key, value in variables.items():
        current_vars[key] = value
    
    # Write the updated file
    with open(file_path, 'w') as f:
        f.write("# Environment variables\n")
        for key, value in sorted(current_vars.items()):
            f.write(f"{key}={value}\n")
    
    print_success(f"Updated {file_path} with {len(variables)} variables")

def pull_railway_variables():
    """Pull environment variables from Railway services."""
    print_section("Railway Variables")
    
    # Get Railway services
    services = get_railway_services()
    
    if not services:
        print_error("No Railway services found.")
        return {}
    
    # Display services
    for i, service in enumerate(services):
        print_info(f"{i+1}. {service.get('name')} ({service.get('id')})")
    
    # Ask which service to pull variables from
    print_info("\nWhich service do you want to pull variables from? (Enter a number)")
    choice = input().strip()
    
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(services):
            print_error("Invalid selection.")
            return {}
        
        selected_service = services[index]
        service_id = selected_service.get('id')
        service_name = selected_service.get('name')
        
        print_info(f"Pulling variables from service: {service_name}")
        
        # Get variables for the service
        variables = get_railway_variables(service_id)
        
        if not variables:
            print_error(f"No variables found for service: {service_name}")
            return {}
        
        print_success(f"Found {len(variables)} variables in service: {service_name}")
        
        # Filter variables for backend
        backend_vars = {}
        for key, value in variables.items():
            if key in [
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
            ]:
                backend_vars[key] = value
        
        return backend_vars
    except ValueError:
        print_error("Invalid input.")
        return {}

def pull_vercel_variables():
    """Pull environment variables from Vercel projects."""
    print_section("Vercel Variables")
    
    try:
        # Check if Vercel CLI is installed and logged in
        vercel_whoami = run_command("vercel whoami")
        if not vercel_whoami:
            print_warning("Vercel CLI not installed or not logged in. Skipping Vercel variables.")
            return {}
        
        # Get Vercel projects
        projects = get_vercel_projects()
        
        if not projects:
            print_error("No Vercel projects found.")
            return {}
        
        # Display projects
        for i, project in enumerate(projects):
            print_info(f"{i+1}. {project.get('name')} ({project.get('id')})")
        
        # Ask which project to pull variables from
        print_info("\nWhich project do you want to pull variables from? (Enter a number)")
        choice = input().strip()
        
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(projects):
                print_error("Invalid selection.")
                return {}
            
            selected_project = projects[index]
            project_id = selected_project.get('id')
            project_name = selected_project.get('name')
            
            print_info(f"Pulling variables from project: {project_name}")
            
            # Get variables for the project
            variables = get_vercel_variables(project_id)
            
            if not variables:
                print_error(f"No variables found for project: {project_name}")
                return {}
            
            print_success(f"Found {len(variables)} variables in project: {project_name}")
            
            # Filter variables for frontend
            frontend_vars = {}
            for key, value in variables.items():
                if key in [
                    "NEXT_PUBLIC_BACKEND_URL",
                    "NEXT_PUBLIC_UPLOADS_URL",
                    "NEXTAUTH_SECRET",
                    "NEXT_PUBLIC_SUPABASE_URL",
                    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
                ]:
                    frontend_vars[key] = value
            
            return frontend_vars
        except ValueError:
            print_error("Invalid input.")
            return {}
    except Exception as e:
        print_error(f"Error pulling Vercel variables: {str(e)}")
        return {}

def main():
    """Main function."""
    print_header("Pull Live Variables")
    
    print_info("This script pulls environment variables from live Railway and Vercel services")
    print_info("and updates the local environment files.")
    print_info("")
    print_info("Make sure you have the Railway CLI and Vercel CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    # Pull Railway variables
    railway_vars = pull_railway_variables()
    
    if railway_vars:
        # Update backend environment files
        update_env_file("backend/.env", railway_vars)
        update_env_file(".env", railway_vars)
        
        # Ask if user wants to update backend/.env.local
        print_info("\nDo you want to update backend/.env.local with Railway variables? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            update_env_file("backend/.env.local", railway_vars)
    
    # Pull Vercel variables
    vercel_vars = pull_vercel_variables()
    
    if vercel_vars:
        # Update frontend environment files
        update_env_file("frontend/.env.local", vercel_vars)
        
        # Ask if user wants to update .env.local
        print_info("\nDo you want to update .env.local with Vercel variables? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            update_env_file(".env.local", vercel_vars)
    
    print_header("Pull Complete")
    print_info("The environment variables have been pulled from live services and updated in local files.")

if __name__ == "__main__":
    main()
