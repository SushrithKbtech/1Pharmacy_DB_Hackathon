import os, json, time, statistics, psycopg2

DB_DSN = os.environ.get(
    "DB_DSN",
    "dbname=pharmacy user=postgres password=postgres host=localhost port=5432"
)

def run_query(cur, typ, q):
    if typ == "prefix":
        cur.execute("SELECT name FROM medicines WHERE name ILIKE %s ORDER BY name LIMIT 5", (q+"%",))
    elif typ == "substring":
        cur.execute("""
            SELECT name FROM medicines
            WHERE name ILIKE %s
            ORDER BY similarity(name, %s) DESC, name LIMIT 5
        """, (f"%{q}%", q))
    elif typ == "fulltext":
        cur.execute("""
            SELECT name FROM medicines
            WHERE fts @@ plainto_tsquery('english', %s)
            ORDER BY ts_rank(fts, plainto_tsquery('english', %s)) DESC, name
            LIMIT 5
        """, (q, q))
    elif typ == "fuzzy":
        cur.execute("SELECT name FROM medicines ORDER BY similarity(name, %s) DESC, name LIMIT 5", (q,))
    else:
        raise ValueError("unknown type")
    return [r[0] for r in cur.fetchall()]

def main():
    with open("benchmark_queries.json","r",encoding="utf-8") as f:
        tests = json.load(f)["tests"]

    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()

    results = {}
    timings = []

    for t in tests:
        typ, q, i = t["type"], t["query"], t["id"]
        run_query(cur, typ, q)  # warm-up
        t0 = time.perf_counter()
        out = run_query(cur, typ, q)
        t1 = time.perf_counter()
        timings.append((typ, q, (t1 - t0) * 1000.0))
        results[str(i)] = out

    with open("submission.json","w",encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=2, ensure_ascii=False)

    lat = [x[2] for x in timings]
    report = {
        "count": len(lat),
        "latency_ms": {
            "min": min(lat),
            "p50": statistics.median(lat),
            "avg": sum(lat)/len(lat),
            "p90": statistics.quantiles(lat, n=10)[8-1],
            "max": max(lat)
        },
        "samples": [{"type": t, "q": q, "latency_ms": ms} for t, q, ms in timings]
    }
    with open("bench_stats.json","w",encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("Wrote submission.json and bench_stats.json")

if __name__ == "__main__":
    main()
