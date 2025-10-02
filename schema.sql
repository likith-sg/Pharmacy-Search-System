-- Enable the trigram extension for efficient fuzzy and substring searches
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create the main table to store medicine data
CREATE TABLE medicines (
    id TEXT PRIMARY KEY,
    sku_id TEXT,
    name TEXT NOT NULL,
    manufacturer_name TEXT,
    short_composition TEXT,
    -- This column will store pre-processed text for full-text search
    search_vector TSVECTOR
);

-- Index for FAST Prefix, Substring, and Fuzzy Search
CREATE INDEX idx_gin_name_trgm ON medicines USING GIN (name gin_trgm_ops);

-- Index for FAST Full-Text Search
CREATE INDEX idx_gin_search_vector ON medicines USING GIN (search_vector);