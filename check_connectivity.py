#!/usr/bin/env python3
"""
Connectivity Check Script for Web Analytics

This script checks the connectivity between different components of the web analytics application:
1. Vercel (Frontend)
2. Railway (Backend)
3. Supabase (Database)

Usage:
    python check_connectivity.py
"""

import os
import sys
import json
import requests
import subprocess
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

def check_env_vars():
    """Check environment variables."""
    print_section("Environment Variables Check")
    
    # Check local environment variables
    env_files = [
        ".env",
        ".env.local",
        ".env.production",
        ".env.vercel.production",
        "backend/.env",
        "backend/.env.local"
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print_info(f"Found environment file: {env_file}")
            
            # Read the file and check for key variables
            with open(env_file, 'r') as f:
                content = f.read()
                
            # Check for key variables
            key_vars = [
                "DATABASE_URL",
                "SUPABASE_URL",
                "SUPABASE_KEY",
                "REDIS_PUBLIC_URL",
                "NEXT_PUBLIC_BACKEND_URL"
            ]
            
            for var in key_vars:
                if var in content:
                    print_success(f"  {var} is defined in {env_file}")
                else:
                    print_warning(f"  {var} is NOT defined in {env_file}")
        else:
            print_warning(f"Environment file not found: {env_file}")
    
    # Check Railway environment variables
    print_info("\nChecking Railway environment variables...")
    try:
        railway_vars = run_command("railway variables list")
        if railway_vars:
            print_success("Successfully retrieved Railway variables")
            
            # Check for key variables in Railway
            for var in key_vars:
                if var in railway_vars:
                    print_success(f"  {var} is defined in Railway")
                else:
                    print_warning(f"  {var} is NOT defined in Railway")
        else:
            print_error("Failed to retrieve Railway variables")
    except Exception as e:
        print_error(f"Error checking Railway variables: {str(e)}")

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

def check_database_connection():
    """Check database connection."""
    print_section("Database Connection Check")
    
    # Get the database URL from environment variables
    db_url = None
    env_files = [".env.vercel.production", ".env.local", "backend/.env.local", ".env"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        db_url = line.strip().split("=", 1)[1].strip('"\'')
                        break
            if db_url:
                break
    
    if not db_url:
        print_error("Could not find DATABASE_URL in environment files")
        return
    
    # Parse the database URL to hide password in output
    parsed_url = urlparse(db_url)
    safe_url = f"{parsed_url.scheme}://{parsed_url.username}:****@{parsed_url.hostname}:{parsed_url.port}{parsed_url.path}"
    print_info(f"Database URL: {safe_url}")
    
    # Check database connection using psql
    try:
        print_info("Testing database connection...")
        # Create a temporary file with the connection command
        with open("temp_db_check.py", "w") as f:
            f.write("""
import os
import sys
import psycopg2
from sqlalchemy import create_engine, text

# Get the database URL from environment variable
db_url = sys.argv[1]

try:
    # Try SQLAlchemy connection
    print("Testing SQLAlchemy connection...")
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("SQLAlchemy connection successful")
        
    # Try psycopg2 connection
    print("\\nTesting psycopg2 connection...")
    parsed_url = db_url.replace("postgresql://", "").split("/")
    db_name = parsed_url[1]
    user_host = parsed_url[0].split("@")
    host_port = user_host[1].split(":")
    user_pass = user_host[0].split(":")
    
    conn = psycopg2.connect(
        dbname=db_name,
        user=user_pass[0],
        password=user_pass[1],
        host=host_port[0],
        port=host_port[1] if len(host_port) > 1 else 5432
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("psycopg2 connection successful")
    cursor.close()
    conn.close()
    
    print("\\nDatabase connection is working properly")
    sys.exit(0)
except Exception as e:
    print(f"Error connecting to database: {str(e)}")
    sys.exit(1)
""")
        
        # Run the script
        result = run_command(f"python temp_db_check.py '{db_url}'")
        if result:
            print_info(result)
        
        # Clean up
        os.remove("temp_db_check.py")
    except Exception as e:
        print_error(f"Error checking database connection: {str(e)}")
        # Clean up
        if os.path.exists("temp_db_check.py"):
            os.remove("temp_db_check.py")

def check_supabase_connection():
    """Check Supabase connection."""
    print_section("Supabase Connection Check")
    
    # Get Supabase URL and key from environment variables
    supabase_url = None
    supabase_key = None
    env_files = [".env.vercel.production", ".env.local", "backend/.env.local", ".env"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
                
                if "SUPABASE_URL=" in content:
                    for line in content.split("\n"):
                        if line.startswith("SUPABASE_URL="):
                            supabase_url = line.strip().split("=", 1)[1].strip('"\'')
                
                if "SUPABASE_KEY=" in content:
                    for line in content.split("\n"):
                        if line.startswith("SUPABASE_KEY="):
                            supabase_key = line.strip().split("=", 1)[1].strip('"\'')
                
            if supabase_url and supabase_key:
                break
    
    if not supabase_url or not supabase_key:
        print_error("Could not find SUPABASE_URL and SUPABASE_KEY in environment files")
        return
    
    print_info(f"Supabase URL: {supabase_url}")
    
    # Check Supabase connection
    try:
        print_info("Testing Supabase connection...")
        # Create a temporary file with the connection check
        with open("temp_supabase_check.py", "w") as f:
            f.write("""
import os
import sys
import requests
import json

# Get Supabase URL and key from arguments
supabase_url = sys.argv[1]
supabase_key = sys.argv[2]

try:
    # Test connection to Supabase REST API
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }
    
    # Try to access the health endpoint
    health_url = f"{supabase_url}/rest/v1/"
    print(f"Testing connection to {health_url}")
    response = requests.get(health_url, headers=headers)
    
    print(f"Status code: {response.status_code}")
    if response.status_code < 400:
        print("Supabase REST API connection successful")
    else:
        print(f"Supabase REST API returned error: {response.status_code}")
        print(response.text)
    
    sys.exit(0)
except Exception as e:
    print(f"Error connecting to Supabase: {str(e)}")
    sys.exit(1)
""")
        
        # Run the script
        result = run_command(f"python temp_supabase_check.py '{supabase_url}' '{supabase_key}'")
        if result:
            print_info(result)
        
        # Clean up
        os.remove("temp_supabase_check.py")
    except Exception as e:
        print_error(f"Error checking Supabase connection: {str(e)}")
        # Clean up
        if os.path.exists("temp_supabase_check.py"):
            os.remove("temp_supabase_check.py")

def check_auth_flow():
    """Check authentication flow."""
    print_section("Authentication Flow Check")
    
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
    
    # Test authentication endpoint
    auth_url = f"{backend_url}/users/json-token"
    print_info(f"Testing authentication endpoint: {auth_url}")
    
    # Ask for test credentials
    print_info("Please enter test credentials for authentication check:")
    email = input("Email: ")
    password = input("Password: ")
    
    try:
        # Test authentication
        print_info("Sending authentication request...")
        start_time = time.time()
        response = requests.post(
            auth_url,
            json={"email": email, "password": password},
            timeout=15
        )
        end_time = time.time()
        
        print_info(f"Request took {end_time - start_time:.2f} seconds")
        print_info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Authentication successful")
            print_info("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print_error(f"Authentication failed with status code: {response.status_code}")
            print_info("Response:")
            print(response.text)
    except requests.exceptions.Timeout:
        print_error(f"Request to {auth_url} timed out")
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to connect to {auth_url}: {str(e)}")

def main():
    """Main function."""
    print_header("Web Analytics Connectivity Check")
    
    print_info("This script will check the connectivity between different components of the web analytics application.")
    print_info("Make sure you have the Railway CLI installed and are logged in.")
    print_info("Press Enter to continue or Ctrl+C to exit.")
    input()
    
    check_env_vars()
    check_railway_status()
    check_api_endpoints()
    check_database_connection()
    check_supabase_connection()
    
    print_info("\nDo you want to check the authentication flow? (y/n)")
    choice = input().lower()
    if choice == 'y':
        check_auth_flow()
    
    print_header("Connectivity Check Complete")

if __name__ == "__main__":
    main()
