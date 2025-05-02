import psycopg2

# Connect to the database
conn = psycopg2.connect(
    "postgresql://postgres:Gunners4ever2804!@db.tipdainlasfkkgwxoexm.supabase.co:5432/postgres"
)

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
