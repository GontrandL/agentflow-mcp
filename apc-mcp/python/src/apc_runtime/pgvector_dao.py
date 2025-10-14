# pgvector DAO (sync) — assumes: CREATE EXTENSION IF NOT EXISTS vector;
# pip install psycopg[binary]
import hashlib
import json
from typing import List, Tuple, Optional
import psycopg

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS expectation_vectors (
  ns TEXT NOT NULL,
  kind TEXT NOT NULL,           -- 'acceptance' | 'constraint' | 'failure_motif'
  text TEXT NOT NULL,
  embedding vector(768) NOT NULL,
  meta JSONB,
  PRIMARY KEY (ns, kind, md5(text))
);
CREATE INDEX IF NOT EXISTS expectation_vectors_ns_idx ON expectation_vectors(ns);
"""

class PgVectorDAO:
    def __init__(self, dsn: str) -> None:
        self.conn = psycopg.connect(dsn, autocommit=True)
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(SCHEMA_SQL)

    @staticmethod
    def _hash_text(s: str) -> str:
        return hashlib.md5(s.encode()).hexdigest()

    def upsert(self, ns: str, kind: str, text: str, emb: List[float], meta: dict | None=None) -> None:
        key = self._hash_text(text)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO expectation_vectors (ns, kind, text, embedding, meta)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (ns, kind, md5(text))
                DO UPDATE SET embedding = EXCLUDED.embedding, meta = EXCLUDED.meta
                """,
                (ns, kind, text, emb, json.dumps(meta or {}))
            )

    def search(self, ns: str, query_emb: List[float], top_k: int=10, kinds: Optional[List[str]]=None
               ) -> List[Tuple[str,float,dict]]:
        where = "ns = %s"
        params = [ns]
        if kinds:
            where += " AND kind = ANY(%s)"
            params.append(kinds)
        sql = f"""
          SELECT text, (embedding <#> %s) AS dist, meta
          FROM expectation_vectors
          WHERE {where}
          ORDER BY embedding <#> %s
          LIMIT %s
        """
        # the "<#>" operator = inner product distance for pgvector
        params = [*params, query_emb, query_emb, top_k]
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [(t, float(d), m) for (t, d, m) in cur.fetchall()]
