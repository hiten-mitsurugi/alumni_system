import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    print("=== All Tables in Database ===")
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    for table in tables:
        print(f"  {table['table_name']}")

    print("\n=== Check auth_app_workhistory Columns ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'auth_app_workhistory'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    if columns:
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']}: {col['data_type']} ({nullable})")
    else:
        print("  Table not found!")

    cursor.close()
    conn.close()
    print("\n✅ Database connection successful!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
