import json
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read credentials securely from the environment
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DATA_DIR = os.path.join("DB_Dataset", "data")

def import_data():
    """Reads data from multiple JSON files and imports it into the database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        insert_query = """
            INSERT INTO medicines (id, sku_id, name, manufacturer_name, short_composition, search_vector)
            VALUES (%s, %s, %s, %s, %s, to_tsvector('english', COALESCE(%s, '') || ' ' || COALESCE(%s, '')))
            ON CONFLICT (id) DO NOTHING;
        """
        print("Starting data import...")
        for filename in sorted(os.listdir(DATA_DIR)):
            if filename.endswith(".json"):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    medicines_list = json.load(f)
                    for med in medicines_list:
                        cur.execute(insert_query, (
                            med.get('id'), med.get('sku_id'), med.get('name'),
                            med.get('manufacturer_name'), med.get('short_composition'),
                            med.get('name'), med.get('short_composition')
                        ))
        conn.commit()
        print("Data import completed successfully.")
    except Exception as error:
        print(f"Error during data import: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    import_data()