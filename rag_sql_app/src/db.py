import psycopg2
from psycopg2.extras import RealDictCursor
from .config import POSTGRES_CONFIG


FORBIDDEN_SQL = ["insert", "update", "delete", "drop", "alter", "truncate"]


def validate_sql(sql: str):
    sql_l = sql.lower().strip()
    if not sql_l.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    if any(word in sql_l for word in FORBIDDEN_SQL):
        raise ValueError("Unsafe SQL detected")


class PostgresAdapter:
    def __init__(self):
        self.conn = psycopg2.connect(**POSTGRES_CONFIG)
        self.conn.autocommit = True

    def execute(self, sql: str):
        validate_sql(sql)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SET statement_timeout = 5000;")
            cur.execute(sql)
            return cur.fetchall()