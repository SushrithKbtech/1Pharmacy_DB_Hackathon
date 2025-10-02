import os, glob, json, psycopg2

DB_DSN = os.environ.get(
    "DB_DSN",
    "dbname=pharmacy user=postgres password=postgres host=localhost port=5432"
)
DATA_DIR = os.environ.get("DATA_DIR", "./data")

def yield_records(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for rec in data:
            yield (
                rec.get("id"),
                rec.get("sku_id"),
                rec.get("name"),
                rec.get("manufacturer_name"),
                rec.get("marketer_name"),
                rec.get("type"),
                rec.get("price"),
                rec.get("pack_size_label"),
                rec.get("short_composition"),
                rec.get("is_discontinued"),
                rec.get("available"),
                rec.get("slug"),
                rec.get("image_url"),
            )

def main():
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()

    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    total = 0
    for fp in files:
        batch = list(yield_records(fp))
        if not batch:
            continue
        args = b",".join(
            cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", row)
            for row in batch if row[0] is not None
        )
        cur.execute(
            b"""
            INSERT INTO medicines
            (id, sku_id, name, manufacturer_name, marketer_name, type, price,
             pack_size_label, short_composition, is_discontinued, available, slug, image_url)
            VALUES
            """ + args + b"""
            ON CONFLICT (id) DO NOTHING
            """
        )
        conn.commit()
        total += len(batch)
        print(f"Inserted {len(batch)} from {os.path.basename(fp)} (total={total})")

    # Backfill FTS once after load (trigger handles subsequent updates)
    cur.execute("""
        UPDATE medicines
        SET fts =
          setweight(to_tsvector('english', unaccent(coalesce(name,''))), 'A')
          || setweight(to_tsvector('english', unaccent(coalesce(short_composition,''))), 'B')
          || setweight(to_tsvector('english', unaccent(coalesce(type,''))), 'C')
          || setweight(to_tsvector('english', unaccent(coalesce(manufacturer_name,''))), 'D')
    """)
    conn.commit()
    cur.close(); conn.close()
    print("Done import.")

if __name__ == "__main__":
    main()
