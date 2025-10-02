# Pharmacy Search System

This project is a high-performance search system for a medicine dataset, implemented using PostgreSQL and FastAPI. It supports prefix, substring, full-text, and fussy (typo-tolerant) search functionalities.

## 1. Technical Approach

The core of this system is a PostgreSQL database optimized for various types of text searches.

* **Indexing**: A GIN index with the `pg_trgm` extension is used on the `name` column to efficiently handle prefix, substring, and fussy searches. For full-text search, a dedicated `tsvector` column with its own GIN index handles language-aware queries.
* **API**: The REST API is built with FastAPI for high performance and includes auto-generated interactive documentation.
* **Configuration**: Database credentials are managed securely using environment variables loaded from a `.env` file.

## 2. Benchmark Report

### Methodology

The benchmarks were run locally. API latency was measured using a Python script. PostgreSQL's `EXPLAIN ANALYZE` was used to confirm index usage. On the provided dataset, the query planner correctly utilized the GIN indexes for optimal performance after the table statistics were updated with the `ANALYZE` command.

### Performance Results

| Search Type | Query    | Index Used              |
| :---------- | :------- | :---------------------- |
| Prefix      | `boc`    | `idx_gin_name_trgm`     |
| Substring   | `Leekuf` | `idx_gin_name_trgm`     |
| Fussy       | `daxid`  | `idx_gin_name_trgm`     |
| Full-Text   | `cancer` | `idx_gin_search_vector` |

## 3. Setup and Run Instructions

### Prerequisites

* Python 3.8+
* PostgreSQL
* Git

### Clone the Repository

```bash
git clone [Your GitHub Repository URL]
cd [Your Project Folder Name]
```

### Set Up the Python Environment

Create and activate a virtual environment, then install dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Configure the Database

Ensure your PostgreSQL server is running.

* Create a new database (e.g., `pharmacy_db`).
* Create a `.env` file and fill in your database credentials.
* Connect to your database and run the contents of `schema.sql` to create the tables and indexes. Remember to run:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

first.

### Import Data

Run the import script to populate the database. This is a one-time step.

```bash
python import_data.py
```

### Run the API Server

Start the FastAPI application using Uvicorn.

```bash
uvicorn main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

The interactive documentation is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
