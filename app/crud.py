from .database import get_conn

def q_prefix(q: str, limit: int = 20):
    sql = "SELECT name FROM medicines WHERE name ILIKE %s ORDER BY name LIMIT %s"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (q + "%", limit))
        return [r[0] for r in cur.fetchall()]

def q_substring(q: str, limit: int = 20):
    sql = """
      SELECT name
      FROM medicines
      WHERE name ILIKE %s
      ORDER BY similarity(name, %s) DESC, name
      LIMIT %s
    """
    like = f"%{q}%"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (like, q, limit))
        return [r[0] for r in cur.fetchall()]

def q_fulltext(q: str, limit: int = 20):
    sql = """
      SELECT name
      FROM medicines
      WHERE fts @@ plainto_tsquery('english', %s)
      ORDER BY ts_rank(fts, plainto_tsquery('english', %s)) DESC, name
      LIMIT %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (q, q, limit))
        return [r[0] for r in cur.fetchall()]

def q_fuzzy(q: str, limit: int = 20):
    sql = "SELECT name FROM medicines ORDER BY similarity(name, %s) DESC, name LIMIT %s"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (q, limit))
        return [r[0] for r in cur.fetchall()]
