-- ============================================================
-- PaaS Lab 2026 — Database Schema (Railway-managed PostgreSQL)
-- ============================================================

-- Table: sentiment_logs
-- Stores every sentiment analysis request for CRUD demonstration.
-- Created automatically by Flask-SQLAlchemy on first run.

CREATE TABLE IF NOT EXISTS sentiment_logs (
    id          SERIAL PRIMARY KEY,
    input_text  VARCHAR(500)    NOT NULL,
    sentiment   VARCHAR(20)     NOT NULL,   -- 'positive', 'negative', 'neutral'
    greeting    TEXT            NOT NULL,
    created_at  TIMESTAMP       DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- ============================================================
-- Sample Data
-- ============================================================

INSERT INTO sentiment_logs (input_text, sentiment, greeting, created_at) VALUES
    ('I am happy and excited',   'positive', 'Hello, I am happy and excited! Your enthusiasm is wonderful — welcome to our PaaS Lab!', '2026-04-01 10:00:00'),
    ('This is terrible and sad', 'negative', 'Hello, This is terrible and sad. We hope this experience brightens your day. Welcome to our PaaS Lab.', '2026-04-01 10:05:00'),
    ('Cloud computing rocks',    'neutral',  'Hello, Cloud computing rocks! Welcome to our PaaS Lab.', '2026-04-01 10:10:00'),
    ('I love amazing technology','positive', 'Hello, I love amazing technology! Your enthusiasm is wonderful — welcome to our PaaS Lab!', '2026-04-01 10:15:00'),
    ('frustrated with debugging','negative', 'Hello, frustrated with debugging. We hope this experience brightens your day. Welcome to our PaaS Lab.', '2026-04-01 10:20:00');

-- ============================================================
-- CRUD Operations Reference
-- ============================================================

-- CREATE: Automatically via POST /greet or POST /api/analyse
-- READ:   GET /logs (HTML) or GET /api/logs (JSON)
-- UPDATE: PUT /api/logs/<id> with JSON body {"input_text": "new text"}
-- DELETE: DELETE /api/logs/<id>
