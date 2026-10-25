-- Migração 001: tabelas base alinhadas a docs/dados/esquema.md.
-- Sem FTS5 nem sqlite-vec (ficam para 002 / PLN-07).

CREATE TABLE documentos (
    id INTEGER PRIMARY KEY,
    caminho TEXT NOT NULL UNIQUE,
    titulo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    tipo_sugerido TEXT,
    sha256 TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('ok', 'desactualizado', 'a_indexar', 'erro')),
    paginas INTEGER,
    miniatura_caminho TEXT,
    sumario_json TEXT,
    criado_em TEXT NOT NULL,
    actualizado_em TEXT NOT NULL,
    indexado_em TEXT
);

CREATE INDEX idx_documentos_estado ON documentos (estado);
CREATE INDEX idx_documentos_tipo ON documentos (tipo);
CREATE INDEX idx_documentos_sha256 ON documentos (sha256);

CREATE TABLE documento_hashes (
    id INTEGER PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    sha256 TEXT NOT NULL,
    visto_em TEXT NOT NULL,
    activa INTEGER NOT NULL CHECK (activa IN (0, 1)),
    UNIQUE (documento_id, sha256)
);

CREATE INDEX idx_documento_hashes_doc ON documento_hashes (documento_id, activa);
CREATE INDEX idx_documento_hashes_sha ON documento_hashes (sha256);

CREATE TABLE blocos (
    id INTEGER PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    hash_id INTEGER NOT NULL REFERENCES documento_hashes (id) ON DELETE CASCADE,
    ordem INTEGER NOT NULL,
    texto TEXT NOT NULL,
    pagina_inicio INTEGER,
    pagina_fim INTEGER,
    offset_inicio INTEGER NOT NULL,
    offset_fim INTEGER NOT NULL,
    tokens_aprox INTEGER NOT NULL,
    UNIQUE (hash_id, ordem)
);

CREATE INDEX idx_blocos_documento ON blocos (documento_id);
CREATE INDEX idx_blocos_hash_ordem ON blocos (hash_id, ordem);

CREATE TABLE frases (
    id INTEGER PRIMARY KEY,
    bloco_id INTEGER NOT NULL REFERENCES blocos (id) ON DELETE CASCADE,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    pagina INTEGER,
    texto TEXT NOT NULL,
    offset_inicio INTEGER NOT NULL,
    offset_fim INTEGER NOT NULL,
    caixas_json TEXT,
    ordem INTEGER NOT NULL
);

CREATE INDEX idx_frases_bloco ON frases (bloco_id, ordem);
CREATE INDEX idx_frases_documento_pagina ON frases (documento_id, pagina);

CREATE TABLE conversas (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    actualizado_em TEXT NOT NULL,
    apagada INTEGER NOT NULL DEFAULT 0 CHECK (apagada IN (0, 1))
);

CREATE INDEX idx_conversas_actualizado ON conversas (actualizado_em DESC);

CREATE TABLE mensagens (
    id INTEGER PRIMARY KEY,
    conversa_id INTEGER NOT NULL REFERENCES conversas (id) ON DELETE CASCADE,
    papel TEXT NOT NULL CHECK (papel IN ('utilizador', 'assistente', 'sistema')),
    modo TEXT CHECK (
        modo IS NULL
        OR modo IN ('procurar', 'correlacionar', 'confrontar', 'alerta', 'lacunas')
    ),
    lente TEXT CHECK (
        lente IS NULL
        OR lente IN ('investigar', 'assessment', 'acreditacao', 'verificar')
    ),
    conteudo TEXT NOT NULL,
    meta_json TEXT,
    criado_em TEXT NOT NULL
);

CREATE INDEX idx_mensagens_conversa ON mensagens (conversa_id, id);

CREATE TABLE citacoes (
    id INTEGER PRIMARY KEY,
    mensagem_id INTEGER NOT NULL REFERENCES mensagens (id) ON DELETE CASCADE,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE RESTRICT,
    frase_id INTEGER REFERENCES frases (id) ON DELETE SET NULL,
    indice INTEGER NOT NULL,
    trecho_literal TEXT NOT NULL,
    ficheiro TEXT NOT NULL,
    pagina INTEGER,
    offset_inicio INTEGER,
    offset_fim INTEGER,
    caixas_json TEXT,
    pontuacao_juiz REAL,
    sha256_ficheiro TEXT
);

CREATE INDEX idx_citacoes_mensagem ON citacoes (mensagem_id, indice);

CREATE TABLE trechos_fixados (
    id INTEGER PRIMARY KEY,
    mensagem_id INTEGER NOT NULL REFERENCES mensagens (id) ON DELETE CASCADE,
    conversa_id INTEGER NOT NULL REFERENCES conversas (id) ON DELETE CASCADE,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE RESTRICT,
    frase_id INTEGER REFERENCES frases (id) ON DELETE SET NULL,
    trecho_literal TEXT NOT NULL,
    ficheiro TEXT NOT NULL,
    pagina INTEGER,
    offset_inicio INTEGER,
    offset_fim INTEGER,
    caixas_json TEXT,
    fixado_em TEXT NOT NULL
);

CREATE INDEX idx_trechos_fixados_mensagem ON trechos_fixados (mensagem_id);
CREATE INDEX idx_trechos_fixados_conversa ON trechos_fixados (conversa_id);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    mensagem_id INTEGER REFERENCES mensagens (id) ON DELETE SET NULL,
    pergunta TEXT NOT NULL,
    trecho TEXT NOT NULL,
    etiqueta TEXT NOT NULL CHECK (etiqueta IN ('positivo', 'negativo')),
    lente TEXT,
    hash_par TEXT NOT NULL UNIQUE,
    documento_id INTEGER REFERENCES documentos (id) ON DELETE SET NULL,
    frase_id INTEGER REFERENCES frases (id) ON DELETE SET NULL,
    origem TEXT NOT NULL CHECK (origem IN ('local', 'importado')),
    criado_em TEXT NOT NULL
);

CREATE INDEX idx_feedback_lente ON feedback (lente);
CREATE INDEX idx_feedback_criado ON feedback (criado_em);

CREATE TABLE dossiers (
    id INTEGER PRIMARY KEY,
    conversa_id INTEGER NOT NULL REFERENCES conversas (id) ON DELETE RESTRICT,
    titulo TEXT NOT NULL,
    fechado_em TEXT NOT NULL,
    perguntas_json TEXT NOT NULL,
    frases_json TEXT NOT NULL,
    ficheiros_json TEXT NOT NULL,
    versao_embedding TEXT NOT NULL,
    versao_juiz TEXT NOT NULL,
    versao_e2b TEXT NOT NULL,
    export_json TEXT
);

CREATE INDEX idx_dossiers_conversa ON dossiers (conversa_id);
CREATE INDEX idx_dossiers_fechado ON dossiers (fechado_em DESC);

CREATE TABLE alertas (
    id INTEGER PRIMARY KEY,
    consulta TEXT NOT NULL,
    lente TEXT,
    activo INTEGER NOT NULL CHECK (activo IN (0, 1)),
    conversa_id INTEGER NOT NULL REFERENCES conversas (id) ON DELETE RESTRICT,
    criado_em TEXT NOT NULL,
    actualizado_em TEXT NOT NULL
);

CREATE INDEX idx_alertas_activo ON alertas (activo);

CREATE TABLE diario (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (
        tipo IN ('procura', 'abertura', 'feedback', 'fecho_dossier')
    ),
    payload_json TEXT NOT NULL,
    criado_em TEXT NOT NULL
);

CREATE INDEX idx_diario_tipo_em ON diario (tipo, criado_em);
CREATE INDEX idx_diario_criado ON diario (criado_em);

CREATE TABLE etiquetas (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    criado_em TEXT NOT NULL
);

CREATE TABLE documento_etiquetas (
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    etiqueta_id INTEGER NOT NULL REFERENCES etiquetas (id) ON DELETE CASCADE,
    PRIMARY KEY (documento_id, etiqueta_id)
);

CREATE INDEX idx_documento_etiquetas_etiqueta ON documento_etiquetas (etiqueta_id);

CREATE TABLE versoes_modelo (
    id INTEGER PRIMARY KEY,
    papel TEXT NOT NULL CHECK (papel IN ('embedding', 'juiz', 'e2b')),
    modelo_id TEXT NOT NULL,
    revisao TEXT NOT NULL,
    lora_id TEXT,
    activo INTEGER NOT NULL CHECK (activo IN (0, 1)),
    notas TEXT,
    registado_em TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_versoes_modelo_unico
    ON versoes_modelo (papel, modelo_id, revisao, IFNULL(lora_id, ''));
CREATE INDEX idx_versoes_activo ON versoes_modelo (papel, activo);

CREATE TABLE fila (
    id INTEGER PRIMARY KEY,
    documento_id INTEGER NOT NULL REFERENCES documentos (id) ON DELETE CASCADE,
    estado TEXT NOT NULL CHECK (
        estado IN ('pendente', 'em_curso', 'concluido', 'erro')
    ),
    prioridade INTEGER NOT NULL DEFAULT 100,
    erro_mensagem TEXT,
    criado_em TEXT NOT NULL,
    iniciado_em TEXT,
    concluido_em TEXT
);

CREATE INDEX idx_fila_estado_prio ON fila (estado, prioridade, id);
