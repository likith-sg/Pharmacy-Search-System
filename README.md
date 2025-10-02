# Pharmacy Search System

This project is a high-performance search system for a medicine dataset, implemented using PostgreSQL and FastAPI. It supports prefix, substring, full-text, and fussy (typo-tolerant) search functionalities.

## 1. Technical Approach

The core of this project is an optimized PostgreSQL database designed for complex text queries. The primary goal was to ensure high performance and low latency across all required search types.

* **Database**: **PostgreSQL** was selected due to its advanced indexing capabilities and support for powerful extensions like `pg_trgm`.

* **Indexing Strategy**: A multi-index approach was used to ensure each search type was handled by a specialized, high-performance index.

  * A **GIN (Generalized Inverted Index)** with the **`pg_trgm`** extension was created on the `name` column. This single index is highly efficient and accelerates three distinct search types: prefix (`ILIKE 'query%'`), substring (`ILIKE '%query%'`), and fussy search (using the `%%` trigram similarity operator).
  * For full-text search, a dedicated **`tsvector`** column (`search_vector`) was pre-populated with processed text from the `name` and `short_composition` fields. This column has its own GIN index, which enables fast, language-aware searching that understands stemming and relevance.

* **API**: The REST API was built with **FastAPI** for its asynchronous performance, data validation with Pydantic, and automatic generation of interactive API documentation.

* **Configuration**: To maintain security and flexibility, database credentials are not hardcoded. They are managed via a `.env` file, which is loaded at runtime and excluded from version control via `.gitignore`.

## 2. Benchmark Report

### Methodology

Performance was benchmarked on a local machine. The `benchmark.py` script was used to measure API **latency** (single-request response time) and **throughput** (concurrent requests per second). PostgreSQL's `EXPLAIN ANALYZE` command was used to verify that the correct indexes were being utilized for each query, confirming that inefficient sequential scans were avoided after updating table statistics.

### Performance Results

| Search Type | Query        | Index Used              | Latency (ms) | Throughput (req/s) |
| :---------- | :----------- | :---------------------- | :----------- | :----------------- |
| Prefix      | `Ava`        | `idx_gin_name_trgm`     | 87.72        | 23.52              |
| Substring   | `Injection`  | `idx_gin_name_trgm`     | 237.17       | 10.70              |
| Fussy       | `Avastn`     | `idx_gin_name_trgm`     | 41.53        | 23.64              |
| Full-Text   | `antibiotic` | `idx_gin_search_vector` | 41.36        | 24.80              |

## 3. Setup and Run Instructions

To set up and run this project, please follow these steps.

### Prerequisites

* Python 3.8+
* PostgreSQL Server
* Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/likith-sg/Pharmacy-Search-System.git
cd Pharmacy-Search-System
```

### Step 2: Set Up the Python Environment

Create and activate a virtual environment, then install the required dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install required packages from the requirements file
pip install -r requirements.txt
```

### Step 3: Configure the Database

Ensure your PostgreSQL server is running.

* Create a new, empty database (e.g., `pharmacy_db`).
* In the project root, create a file named `.env` and populate it with your database credentials.
* Connect to your database and execute the `schema.sql` script to create the tables and indexes. You can do this by running the command below in your terminal, or by pasting the contents of `schema.sql` into a GUI client like pgAdmin.

```bash
# Replace [user] and [database] with your credentials
psql -U [user] -d [database] -f schema.sql
```

### Step 4: Import the Dataset

Run the provided script to populate the database with the medicine data. This is a one-time setup step.

```bash
python import_data.py
```

### Step 5: Run the API Server

Start the FastAPI application using Uvicorn. The server will automatically reload on code changes.

```bash
uvicorn main:app --reload
```

The API is now running and available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Step 6: Verify and Evaluate

* **Interactive Documentation**: You can explore and test all API endpoints interactively by navigating to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your web browser.
* **Run Performance Benchmark (Optional)**: To reproduce the performance metrics, run the `benchmark.py` script. The results will be printed to the terminal and also saved to a timestamped file in the `logs/` directory.

```bash
python benchmark.py
```

* **Generate Submission File**: With the server running, open a second terminal, activate the virtual environment, and run the `generate_submission.py` script to create the final `submission.json` file.

```bash
python generate_submission.py
```
