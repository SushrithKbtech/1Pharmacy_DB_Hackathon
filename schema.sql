-- schema.sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

DROP TABLE IF EXISTS medicines CASCADE;

CREATE TABLE medicines (
    id BIGINT PRIMARY KEY,
    sku_id BIGINT,
    name TEXT NOT NULL,
    manufacturer_name TEXT,
    marketer_name TEXT,
    type TEXT,
    price NUMERIC,
    pack_size_label TEXT,
    short_composition TEXT,
    is_discontinued BOOLEAN,
    available BOOLEAN,
    slug TEXT,
    image_url TEXT,
    fts tsvector
);

-- Prefix search (left-anchored LIKE/ILIKE)
CREATE INDEX IF NOT EXISTS idx_medicines_name_prefix ON medicines (name text_pattern_ops);

-- Substring / fuzzy (trigram)
CREATE INDEX IF NOT EXISTS idx_medicines_name_trgm ON medicines USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_medicines_pack_trgm ON medicines USING gin (pack_size_label gin_trgm_ops);

-- Full-text index
CREATE INDEX IF NOT EXISTS idx_medicines_fts ON medicines USING gin (fts);

-- Trigger to keep fts updated
CREATE OR REPLACE FUNCTION medicines_fts_trigger() RETURNS trigger AS $$
BEGIN
  NEW.fts :=
    setweight(to_tsvector('english', unaccent(coalesce(NEW.name,''))), 'A')
    || setweight(to_tsvector('english', unaccent(coalesce(NEW.short_composition,''))), 'B')
    || setweight(to_tsvector('english', unaccent(coalesce(NEW.type,''))), 'C')
    || setweight(to_tsvector('english', unaccent(coalesce(NEW.manufacturer_name,''))), 'D');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_medicines_fts ON medicines;
CREATE TRIGGER trg_medicines_fts
BEFORE INSERT OR UPDATE ON medicines
FOR EACH ROW EXECUTE FUNCTION medicines_fts_trigger();
