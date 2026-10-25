-- Migração 002: FTS5 + tabela de vectores 256-d (cosseno exacto; PLN-07).
-- A extensão sqlite-vec carrega-se em runtime (engine/pesquisa/vec.py).
-- Não se cria Vec1 nem outro índice aproximado.

CREATE VIRTUAL TABLE fts_texto USING fts5(
    texto,
    origem UNINDEXED,
    origem_id UNINDEXED,
    documento_id UNINDEXED,
    hash_id UNINDEXED,
    tokenize = 'unicode61'
);

CREATE TABLE vectores (
    bloco_id INTEGER PRIMARY KEY REFERENCES blocos (id) ON DELETE CASCADE,
    hash_id INTEGER NOT NULL REFERENCES documento_hashes (id) ON DELETE CASCADE,
    dimensoes INTEGER NOT NULL CHECK (dimensoes = 256),
    embedding BLOB NOT NULL
);

CREATE INDEX idx_vectores_hash ON vectores (hash_id);
