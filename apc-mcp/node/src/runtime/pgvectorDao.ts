// npm i pg
import { Client } from "pg";

const SCHEMA_SQL = `
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS expectation_vectors (
  ns TEXT NOT NULL,
  kind TEXT NOT NULL,
  text TEXT NOT NULL,
  embedding vector(768) NOT NULL,
  meta JSONB,
  PRIMARY KEY (ns, kind, md5(text))
);
CREATE INDEX IF NOT EXISTS expectation_vectors_ns_idx ON expectation_vectors(ns);
`;

export class PgVectorDAO {
  private client: Client;
  constructor(connStr: string) {
    this.client = new Client({ connectionString: connStr });
  }
  async init() {
    await this.client.connect();
    await this.client.query(SCHEMA_SQL);
  }
  async upsert(ns: string, kind: string, text: string, emb: number[], meta: any = {}) {
    const sql = `
      INSERT INTO expectation_vectors (ns, kind, text, embedding, meta)
      VALUES ($1,$2,$3,$4,$5)
      ON CONFLICT (ns, kind, md5(text))
      DO UPDATE SET embedding = EXCLUDED.embedding, meta = EXCLUDED.meta
    `;
    await this.client.query(sql, [ns, kind, text, emb, meta]);
  }
  async search(ns: string, queryEmb: number[], topK = 10, kinds?: string[]) {
    // inner product distance <#>
    const where = kinds?.length ? `ns = $1 AND kind = ANY($2)` : `ns = $1`;
    const params: any[] = kinds?.length ? [ns, kinds, queryEmb, topK] : [ns, queryEmb, topK];
    const sql = `
      SELECT text, (embedding <#> ${kinds?.length ? '$3' : '$2'}) AS dist, meta
      FROM expectation_vectors
      WHERE ${where}
      ORDER BY embedding <#> ${kinds?.length ? '$3' : '$2'}
      LIMIT ${kinds?.length ? '$4' : '$3'}
    `;
    const { rows } = await this.client.query(sql, params);
    return rows as { text: string; dist: number; meta: any }[];
  }
  async close() { await this.client.end(); }
}
