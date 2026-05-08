import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    conn.autocommit = True
    with open("supabase_schema.sql", "r") as f:
        sql = f.read()
    conn.cursor().execute(sql)
    print("Schema created successfully!")
except Exception as e:
    print(f"Error creating schema: {e}")
