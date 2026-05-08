import os
import json
import logging
import psycopg2
import psycopg2.extras
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Load environment variables
load_dotenv()
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT", "5432")
db_name = os.environ.get("DB_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")

if not all([db_host, db_name, db_user, db_password]):
    logging.error("Missing database connection variables in .env")
    exit(1)

OUTPUT_DIR = "output"

def load_data():
    """Iterate over all JSON files and upload them to Supabase via psycopg2."""
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return

    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.startswith('winners_') and f.endswith('.json')])
    
    for filename in files:
        year = int(filename.split('_')[1].split('.')[0])
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        logging.info(f"Processing Year: {year} ({len(data)} constituencies)")
        
        # 1. Insert into elections table
        try:
            # We don't have total electorate/votes strictly at the top level for all years, 
            # we will calculate it from the constituencies
            total_electorate = sum(c.get('electorate', 0) or 0 for c in data)
            total_votes = sum(c.get('votes_polled', 0) or 0 for c in data)
            
            cursor.execute("""
                INSERT INTO elections (year, total_constituencies, total_electorate, total_votes_polled)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (year) DO UPDATE SET
                    total_constituencies = EXCLUDED.total_constituencies,
                    total_electorate = EXCLUDED.total_electorate,
                    total_votes_polled = EXCLUDED.total_votes_polled
            """, (year, len(data), total_electorate, total_votes))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Error inserting election year {year}: {e}")
            continue

        # 2. Insert Constituencies and Candidates
        for const in data:
            const_name = const.get('constituency_name', '').strip()
            
            # Prepare constituency data
            const_data = {
                "election_year": year,
                "constituency_number": str(const.get('constituency_id', '')),
                "constituency_name": const_name,
                "seats": const.get('seats', 1),
                "electorate": const.get('electorate', 0) or 0,
                "votes_polled": const.get('votes_polled', 0) or 0,
                "nota_votes": const.get('nota_votes', 0) or 0
            }
            
            try:
                # Upsert constituency (requires unique constraint on year+name)
                cursor.execute("""
                    INSERT INTO constituencies (election_year, constituency_number, constituency_name, seats, electorate, votes_polled, nota_votes)
                    VALUES (%(election_year)s, %(constituency_number)s, %(constituency_name)s, %(seats)s, %(electorate)s, %(votes_polled)s, %(nota_votes)s)
                    ON CONFLICT (election_year, constituency_name) DO UPDATE SET
                        constituency_number = EXCLUDED.constituency_number,
                        seats = EXCLUDED.seats,
                        electorate = EXCLUDED.electorate,
                        votes_polled = EXCLUDED.votes_polled,
                        nota_votes = EXCLUDED.nota_votes
                    RETURNING id
                """, const_data)
                
                res = cursor.fetchone()
                if res and res.get('id'):
                    const_uuid = res['id']
                else:
                    logging.warning(f"  Could not get UUID for {const_name} ({year})")
                    conn.rollback()
                    continue
                    
                # Prepare candidates
                candidates_to_insert = []
                for cand in const.get('all_candidates', []):
                    candidates_to_insert.append((
                        const_uuid,
                        cand.get('name', 'Unknown'),
                        cand.get('sex', 'N/A'),
                        cand.get('party', 'IND'),
                        cand.get('votes', 0),
                        cand.get('percentage', 0.0),
                        cand.get('rank', 999)
                    ))
                
                if candidates_to_insert:
                    # First, delete existing candidates for this constituency to avoid duplicates if re-running
                    cursor.execute("DELETE FROM candidates WHERE constituency_id = %s", (const_uuid,))
                    
                    # Bulk insert candidates
                    psycopg2.extras.execute_values(
                        cursor,
                        "INSERT INTO candidates (constituency_id, name, sex, party, votes, vote_percentage, rank) VALUES %s",
                        candidates_to_insert
                    )
                conn.commit()
                    
            except Exception as e:
                conn.rollback()
                logging.error(f"Error inserting constituency {const_name} ({year}): {e}")

    cursor.close()
    conn.close()
    logging.info("Data upload complete!")

if __name__ == "__main__":
    load_data()
