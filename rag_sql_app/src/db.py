import psycopg2
from config import POSTGRES_CONFIG

def run_sql(query: str):
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


