import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

# Load environment variables from the .env file at the start of the application
load_dotenv()

# Read credentials securely from the environment
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Initialize the FastAPI app
app = FastAPI(
    title="Pharmacy Search API",
    description="An API for searching a medicine database with prefix, substring, fuzzy, and full-text search capabilities.",
    version="1.0.0",
)

def get_db_connection():
    """Establishes and returns a database connection using environment variables."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        # This will catch errors like wrong password, host, or if the DB is down
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

@app.get("/search/prefix", tags=["Search"])
async def search_prefix(q: str = Query(..., min_length=2, description="Prefix to search for")):
    """
    Performs prefix search on medicine names. This is efficient for "starts with" queries.
    Example: `/search/prefix?q=Ava`
    """
    sql = "SELECT name FROM medicines WHERE name ILIKE %s ORDER BY name LIMIT 20;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # The '%' is a wildcard for any sequence of characters
                cur.execute(sql, (f"{q}%",))
                results = [row[0] for row in cur.fetchall()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/substring", tags=["Search"])
async def search_substring(q: str = Query(..., min_length=3, description="Substring to search for")):
    """
    Performs substring search using a trigram index. This efficiently finds the query anywhere in the name.
    Example: `/search/substring?q=Injection`
    """
    sql = "SELECT name FROM medicines WHERE name ILIKE %s ORDER BY name LIMIT 20;"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # The GIN trigram index efficiently handles the leading wildcard
                cur.execute(sql, (f"%{q}%",))
                results = [row[0] for row in cur.fetchall()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/fussy", tags=["Search"])
async def search_fuzzy(q: str = Query(..., min_length=3)):
    # This query uses the '%' trigram similarity operator, which is accelerated by the GIN index.
    # It needs the similarity_threshold to be set.
    sql = """
        SELECT name FROM medicines
        WHERE name %% %s
        ORDER BY similarity(name, %s) DESC
        LIMIT 20;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # We can set the threshold for the current transaction
                cur.execute("SET pg_trgm.similarity_threshold = 0.3;")
                # character in psycopg2's string formatting, so we escape it with another '%'.
                cur.execute(sql, (q, q))
                results = [row[0] for row in cur.fetchall()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/fulltext", tags=["Search"])
async def search_full_text(q: str = Query(..., min_length=3, description="Full-text search query")):
    """
    Performs full-text search across the medicine's name and composition.
    Example: `/search/fulltext?q=painkiller`
    """
    sql = """
        SELECT name FROM medicines
        WHERE search_vector @@ websearch_to_tsquery('english', %s)
        ORDER BY name
        LIMIT 20;
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (q,))
                results = [row[0] for row in cur.fetchall()]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))