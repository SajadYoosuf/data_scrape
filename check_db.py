import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "5432")
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
cursor = conn.cursor()

print("--- Data Missing/Zero Check ---")

queries = [
    ("Elections with 0 Total Electorate", "SELECT year FROM elections WHERE total_electorate = 0 OR total_electorate IS NULL"),
    ("Elections with 0 Total Votes Polled", "SELECT year FROM elections WHERE total_votes_polled = 0 OR total_votes_polled IS NULL"),
    ("Constituencies with 0 Electorate", "SELECT count(*) FROM constituencies WHERE electorate = 0 OR electorate IS NULL"),
    ("Constituencies with 0 Votes Polled", "SELECT count(*) FROM constituencies WHERE votes_polled = 0 OR votes_polled IS NULL"),
    ("Constituencies with 0 NOTA Votes", "SELECT count(*) FROM constituencies WHERE nota_votes = 0 OR nota_votes IS NULL"),
    ("Candidates with Missing Sex (N/A or empty)", "SELECT count(*) FROM candidates WHERE sex = 'N/A' OR sex IS NULL OR sex = ''"),
    ("Candidates with 0 Votes", "SELECT count(*) FROM candidates WHERE votes = 0 OR votes IS NULL")
]

for name, q in queries:
    cursor.execute(q)
    res = cursor.fetchall()
    if 'year' in q:
        years = [r[0] for r in res]
        print(f"{name}: {len(years)} years ({years})")
    else:
        print(f"{name}: {res[0][0]}")
        
# Total counts for context
cursor.execute("SELECT count(*) FROM constituencies")
print(f"Total Constituencies in DB: {cursor.fetchone()[0]}")

cursor.execute("SELECT count(*) FROM candidates")
print(f"Total Candidates in DB: {cursor.fetchone()[0]}")

cursor.close()
conn.close()
