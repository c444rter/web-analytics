import os
import psycopg2
from dotenv import load_dotenv
import socket

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variable
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL environment variable is not set.")
    print("Please set it to your Supabase connection string.")
    exit(1)

print(f"Using DATABASE_URL: {database_url}")

# Parse the connection string
try:
    # postgresql://postgres:password@db.tipdainlasfkkgwxoexm.supabase.co:5432/postgres
    parts = database_url.split("://")[1]
    auth, host_port_db = parts.split("@")
    username, password = auth.split(":")
    host_port, dbname = host_port_db.split("/")
    host, port = host_port.split(":")
    
    print(f"Parsed connection string:")
    print(f"  Username: {username}")
    print(f"  Password: {'*' * len(password)}")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {dbname}")
    
    # Try to resolve the hostname
    print(f"\nTrying to resolve hostname: {host}")
    try:
        ip_address = socket.gethostbyname(host)
        print(f"  Resolved to IP: {ip_address}")
    except socket.gaierror:
        print(f"  Failed to resolve hostname: {host}")
        
        # Try to connect to the main Supabase domain
        main_domain = host.replace("db.", "")
        print(f"\nTrying to resolve main domain: {main_domain}")
        try:
            ip_address = socket.gethostbyname(main_domain)
            print(f"  Resolved to IP: {ip_address}")
            
            # Try to connect to the IP address directly
            print(f"\nTrying to connect to IP: {ip_address} on port {port}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                result = s.connect_ex((ip_address, int(port)))
                if result == 0:
                    print(f"  Successfully connected to {ip_address}:{port}!")
                else:
                    print(f"  Failed to connect to {ip_address}:{port}. Error code: {result}")
                s.close()
            except Exception as e:
                print(f"  Error connecting to IP: {str(e)}")
        except socket.gaierror:
            print(f"  Failed to resolve main domain: {main_domain}")
    
    # Try to connect to the database using psycopg2
    print(f"\nTrying to connect to database using psycopg2...")
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=username,
            password=password,
            host=host,
            port=port
        )
        print("  Successfully connected to the database!")
        conn.close()
    except Exception as e:
        print(f"  Failed to connect to the database: {str(e)}")
        
        # Try to connect using the main domain IP
        try:
            main_domain = host.replace("db.", "")
            ip_address = socket.gethostbyname(main_domain)
            print(f"\nTrying to connect to database using IP: {ip_address}...")
            conn = psycopg2.connect(
                dbname=dbname,
                user=username,
                password=password,
                host=ip_address,
                port=port
            )
            print("  Successfully connected to the database using IP!")
            conn.close()
        except Exception as e:
            print(f"  Failed to connect to the database using IP: {str(e)}")
except Exception as e:
    print(f"Error parsing connection string: {str(e)}")
