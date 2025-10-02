# Search API Benchmark Report

## Methodology

The benchmarks were run locally. API latency was measured using a Python script. PostgreSQL's `EXPLAIN ANALYZE` was used to confirm index usage. On the provided dataset, the query planner correctly utilized the GIN indexes for optimal performance after the table statistics were updated with the `ANALYZE` command.

## Performance Results

| Search Type   | Query         | Index Used              |
|---------------|---------------|-------------------------|
| Prefix        | `boc`         | `idx_gin_name_trgm`     |
| Substring     | `Leekuf`      | `idx_gin_name_trgm`     |
| Fussy         | `daxid`       | `idx_gin_name_trgm`     |
| Full-Text     | `cancer`      | `idx_gin_search_vector` |

## Technical Approach

-   **Database**: PostgreSQL was chosen for its robustness and powerful extensions.
-   **Indexing Strategy**:
    -   A **GIN (Generalized Inverted Index)** with the **`pg_trgm`** extension was used on the `name` column. This single index efficiently serves prefix, substring, and fussy search queries by leveraging trigram matching.
    -   For full-text search, a dedicated **`tsvector`** column was created and indexed with its own GIN index. This provides fast, language-aware search capabilities.
-   **API**: A REST API was built using **FastAPI** due to its high performance and automatic interactive documentation.