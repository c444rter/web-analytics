import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Local database connection (update these values for your local database)
LOCAL_DB_URL = "postgresql://postgres:postgres@localhost:5432/my_davids"

# Supabase database connection (from environment variables)
# Using session pooler for IPv4 compatibility
SUPABASE_DB_URL = os.environ.get("DATABASE_URL")

def connect_to_db(connection_string):
    """Connect to a PostgreSQL database and return the connection"""
    try:
        conn = psycopg2.connect(connection_string)
        print(f"Connected to database: {conn.dsn}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def get_all_tables(conn):
    """Get a list of all tables in the database"""
    tables = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name != 'alembic_version'
            """)
            tables = [row[0] for row in cur.fetchall()]
        return tables
    except Exception as e:
        print(f"Error getting tables: {str(e)}")
        return []

def export_table_data(conn, table_name):
    """Export all data from a table"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            # Convert rows to list of dicts
            data = [dict(row) for row in rows]
            return data
    except Exception as e:
        print(f"Error exporting data from {table_name}: {str(e)}")
        return []

def get_primary_key(conn, table_name):
    """Get the primary key column(s) for a table"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.attname
                FROM   pg_index i
                JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                    AND a.attnum = ANY(i.indkey)
                WHERE  i.indrelid = %s::regclass
                AND    i.indisprimary
            """, (table_name,))
            primary_keys = [row[0] for row in cur.fetchall()]
            return primary_keys
    except Exception as e:
        print(f"Error getting primary key for {table_name}: {str(e)}")
        return ["id"]  # Default to 'id' if we can't determine the primary key

def import_table_data(conn, table_name, data, primary_keys):
    """Import data into a table, handling conflicts with primary keys"""
    if not data:
        print(f"No data to import for table {table_name}")
        return 0
    
    try:
        # Get column names from the first row of data
        columns = list(data[0].keys())
        
        # Create placeholders for the SQL query
        placeholders = ", ".join(["%s"] * len(columns))
        column_str = ", ".join(columns)
        
        # Create the ON CONFLICT clause
        if primary_keys:
            conflict_targets = ", ".join(primary_keys)
            update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col not in primary_keys])
            conflict_clause = f" ON CONFLICT ({conflict_targets}) DO UPDATE SET {update_set}"
        else:
            conflict_clause = " ON CONFLICT DO NOTHING"
        
        # Prepare the SQL query
        query = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders}){conflict_clause}"
        
        # Execute the query for each row
        with conn.cursor() as cur:
            count = 0
            for row in data:
                values = [row[col] for col in columns]
                try:
                    cur.execute(query, values)
                    count += 1
                except Exception as e:
                    print(f"Error importing row into {table_name}: {str(e)}")
                    print(f"Row data: {row}")
            
            conn.commit()
            return count
    except Exception as e:
        print(f"Error importing data into {table_name}: {str(e)}")
        conn.rollback()
        return 0

def main():
    # Check if we have the required environment variables
    if not SUPABASE_DB_URL:
        print("ERROR: DATABASE_URL environment variable is not set.")
        return
    
    # Connect to local database
    print("Connecting to local database...")
    local_conn = connect_to_db(LOCAL_DB_URL)
    if not local_conn:
        print("Failed to connect to local database. Please check your connection string.")
        return
    
    # Connect to Supabase database
    print("\nConnecting to Supabase database...")
    try:
        supabase_conn = connect_to_db(SUPABASE_DB_URL)
        if not supabase_conn:
            print("Failed to connect to Supabase database. Please check your connection string.")
            return
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        print("Since we can't connect directly to Supabase from your local machine, we'll export the data to JSON files.")
        supabase_conn = None
    
    # Get all tables from local database
    print("\nGetting tables from local database...")
    tables = get_all_tables(local_conn)
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    
    # Export data from each table
    print("\nExporting data from local database...")
    all_data = {}
    for table in tables:
        print(f"Exporting data from {table}...")
        data = export_table_data(local_conn, table)
        all_data[table] = data
        print(f"Exported {len(data)} rows from {table}")
    
    # Save data to JSON file
    print("\nSaving data to JSON file...")
    with open("database_export.json", "w") as f:
        json.dump(all_data, f, default=str, indent=2)
    print("Data saved to database_export.json")
    
    # If we have a Supabase connection, import the data
    if supabase_conn:
        print("\nImporting data to Supabase...")
        for table, data in all_data.items():
            print(f"Importing data into {table}...")
            primary_keys = get_primary_key(supabase_conn, table)
            count = import_table_data(supabase_conn, table, data, primary_keys)
            print(f"Imported {count} rows into {table}")
        
        print("\nData migration completed successfully!")
    else:
        print("\nSince we couldn't connect to Supabase directly, you'll need to:")
        print("1. Deploy your application to Railway")
        print("2. Use the Railway CLI to run this script on the Railway environment")
        print("   or")
        print("3. Use the Supabase dashboard to import the data manually")
        print("\nTo import the data using the Railway CLI:")
        print("1. Install the Railway CLI: https://docs.railway.app/develop/cli")
        print("2. Log in to Railway: railway login")
        print("3. Link to your project: railway link")
        print("4. Run this script on Railway: railway run python migrate_to_supabase.py")
    
    # Close connections
    if local_conn:
        local_conn.close()
    if supabase_conn:
        supabase_conn.close()

if __name__ == "__main__":
    main()
