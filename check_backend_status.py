#!/usr/bin/env python3
"""
Check Backend Status Script

This script checks if the backend is live and running on Railway.
It also provides detailed information about the service status.

Usage:
    python check_backend_status.py
"""

import os
import sys
import json
import subprocess
import requests
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

def check_railway_status():
    """Check Railway deployment status."""
    print_section("Railway Deployment Status")
    
    try:
        status = run_command("railway status")
        if status:
            print_info("Railway Status:")
            print(status)
        else:
            print_error("Failed to get Railway status")
    except Exception as e:
        print_error(f"Error checking Railway status: {str(e)}")

def check_railway_logs():
    """Check Railway logs."""
    print_section("Railway Logs")
    
    try:
        # Get Railway services
        services = run_command("railway service list --json")
        if not services:
            print_error("Failed to get Railway services")
            return
        
        services_json = json.loads(services)
        
        for service in services_json:
            service_id = service.get('id')
            service_name = service.get('name')
            
            print_info(f"Logs for service: {service_name}")
            
            # Get logs for the service
            logs = run_command(f"railway logs --service {service_id} --limit 20")
            if logs:
                print(logs)
            else:
                print_error(f"Failed to get logs for service: {service_name}")
    except Exception as e:
        print_error(f"Error checking Railway logs: {str(e)}")

def check_api_endpoints():
    """Check API endpoints."""
    print_section("API Endpoints Check")
    
    # Get the backend URL from environment variables
    backend_url = None
    env_files = [".env.vercel.production", ".env.local", ".env"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("NEXT_PUBLIC_BACKEND_URL="):
                        backend_url = line.strip().split("=", 1)[1].strip('"\'')
                        break
            if backend_url:
                break
    
    if not backend_url:
        print_error("Could not find NEXT_PUBLIC_BACKEND_URL in environment files")
        return
    
    print_info(f"Backend URL: {backend_url}")
    
    # Check key endpoints
    endpoints = [
        "/health",
        "/users/me",
        "/dashboard/summary"
    ]
    
    for endpoint in endpoints:
        url = f"{backend_url}{endpoint}"
        try:
            print_info(f"Testing endpoint: {url}")
            response = requests.get(url, timeout=10)
            print_info(f"  Status code: {response.status_code}")
            
            if response.status_code < 400:
                print_success(f"  Endpoint {endpoint} is accessible")
            else:
                print_error(f"  Endpoint {endpoint} returned error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print_error(f"  Failed to connect to {url}: {str(e)}")

def check_railway_up_status():
    """Check Railway up status."""
    print_section("Railway Up Status")
    
    try:
        # Get Railway services
        services = run_command("railway service list --json")
        if not services:
            print_error("Failed to get Railway services")
            return
        
        services_json = json.loads(services)
        
        for service in services_json:
            service_id = service.get('id')
            service_name = service.get('name')
            
            print_info(f"Checking up status for service: {service_name}")
            
            # Get up status for the service
            up_status = run_command(f"railway up --service {service_id} --detach")
            if up_status:
                print_info(f"Up status for service {service_name}:")
                print(up_status)
            else:
                print_error(f"Failed to get up status for service: {service_name}")
    except Exception as e:
        print_error(f"Error checking Railway up status: {str(e)}")

def check_railway_variables():
    """Check Railway environment variables."""
    print_section("Railway Environment Variables")
    
    try:
        # Get Railway services
        services = run_command("railway service list --json")
        if not services:
            print_error("Failed to get Railway services")
            return
        
        services_json = json.loads(services)
        
        for service in services_json:
            service_id = service.get('id')
            service_name = service.get('name')
            
            print_info(f"Environment variables for service: {service_name}")
            
            # Get environment variables for the service
            variables = run_command(f"railway variables get --service {service_id}")
            if variables:
                # Mask sensitive values
                masked_variables = []
                for line in variables.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token', 'url']):
                            masked_variables.append(f"{key}=****")
                        else:
                            masked_variables.append(line)
                    else:
                        masked_variables.append(line)
                
                print('\n'.join(masked_variables))
            else:
                print_error(f"Failed to get environment variables for service: {service_name}")
    except Exception as e:
        print_error(f"Error checking Railway environment variables: {str(e)}")

def main():
    """Main function."""
    print_header("Backend Status Check")
    
    print_info("This script will check if the backend is live and running on Railway.")
    print_info("Make sure you have the Railway CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    check_railway_status()
    check_api_endpoints()
    check_railway_variables()
    check_railway_logs()
    
    print_header("Backend Status Check Complete")

if __name__ == "__main__":
    main()
