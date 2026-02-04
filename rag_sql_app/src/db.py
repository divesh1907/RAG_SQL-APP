import psycopg2
import sqlparse
from psycopg2.extras import RealDictCursor
from .config import settings

class UnsafeSQLError(Exception):
    pass


class PostgresAdapter:
    def __init__(self):
        self._conn = None

    def _connect(self):
        if self._conn is None:
            self._conn = psycopg2.connect(settings.DATABASE_URL)

    def _validate_sql(self, sql: str):
        parsed = sqlparse.parse(sql)
        if not parsed:
            raise UnsafeSQLError("Empty SQL")

        stmt = parsed[0]
        if stmt.get_type() != "SELECT":
            raise UnsafeSQLError("Only SELECT queries are allowed")

    def execute(self, sql: str):
        self._validate_sql(sql)
        self._connect()

        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()