import os, psycopg2
DB_DSN = os.environ.get(
    "DB_DSN",
    "dbname=pharmacy user=postgres password=postgres host=localhost port=5432"
)
def get_conn():
    return psycopg2.connect(DB_DSN)
