import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variable
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL environment variable is not set.")
    print("Please set it to your Supabase connection string.")
    exit(1)

print(f"Using DATABASE_URL: {database_url}")

# Connect to the database
conn = psycopg2.connect(database_url)

# Create a cursor
cur = conn.cursor()

# List all tables in the public schema
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cur.fetchall()
print("Tables in public schema:")
for table in tables:
    print(f"  - {table[0]}")

# Close the connection
conn.close()
