import psycopg2

# Connect to the database
conn = psycopg2.connect(
    "postgresql://postgres:Gunners4ever2804!@db.tipdainlasfkkgwxoexm.supabase.co:5432/postgres"
)

# Create a cursor
cur = conn.cursor()

# Check if alembic_version table exists
cur.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'alembic_version')")
alembic_version_exists = cur.fetchone()[0]
print(f"alembic_version table exists: {alembic_version_exists}")

if alembic_version_exists:
    # Check the current version
    cur.execute("SELECT version_num FROM alembic_version")
    version = cur.fetchone()[0]
    print(f"Current alembic version: {version}")

# List all tables in the public schema
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cur.fetchall()
print("Tables in public schema:")
for table in tables:
    print(f"  - {table[0]}")

# Close the connection
conn.close()
