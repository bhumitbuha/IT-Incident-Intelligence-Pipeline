PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS v_ticket_full;
DROP TABLE IF EXISTS ticket_keywords;
DROP TABLE IF EXISTS resolution_metrics;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS kb_keywords;
DROP TABLE IF EXISTS kb_articles;
DROP TABLE IF EXISTS ticket_categories;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id      TEXT PRIMARY KEY,
    dept_name    TEXT NOT NULL,
    location     TEXT
);

CREATE TABLE users (
    user_id      TEXT PRIMARY KEY,
    full_name    TEXT NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    dept_id      TEXT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE assets (
    asset_id           TEXT PRIMARY KEY,
    asset_tag          TEXT UNIQUE NOT NULL,
    model              TEXT NOT NULL,
    asset_type         TEXT NOT NULL,
    purchase_date      TEXT,
    warranty_end       TEXT,
    assigned_user_id   TEXT,
    compliance_status  TEXT,
    age_years          REAL,
    FOREIGN KEY (assigned_user_id) REFERENCES users(user_id)
);

CREATE TABLE ticket_categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);

CREATE TABLE tickets (
    ticket_id          TEXT PRIMARY KEY,
    opened_at          TEXT NOT NULL,
    closed_at          TEXT,
    status             TEXT NOT NULL,
    priority           TEXT NOT NULL,
    category_id        INTEGER,
    short_description  TEXT,
    resolution_notes   TEXT,
    reporter_user_id   TEXT,
    asset_tag          TEXT,
    resolution_hours   REAL,
    sla_breached       INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES ticket_categories(category_id),
    FOREIGN KEY (reporter_user_id) REFERENCES users(user_id),
    FOREIGN KEY (asset_tag) REFERENCES assets(asset_tag)
);

CREATE TABLE ticket_keywords (
    ticket_id    TEXT NOT NULL,
    keyword      TEXT NOT NULL,
    PRIMARY KEY (ticket_id, keyword),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

CREATE TABLE kb_articles (
    kb_id        TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    category     TEXT,
    keywords     TEXT,
    body         TEXT
);

CREATE TABLE kb_keywords (
    kb_id        TEXT NOT NULL,
    keyword      TEXT NOT NULL,
    PRIMARY KEY (kb_id, keyword),
    FOREIGN KEY (kb_id) REFERENCES kb_articles(kb_id)
);

CREATE TABLE resolution_metrics (
    metric_date       TEXT NOT NULL,
    category_name     TEXT NOT NULL,
    priority          TEXT NOT NULL,
    ticket_count      INTEGER NOT NULL,
    avg_resolution_hr REAL,
    breaches          INTEGER NOT NULL,
    PRIMARY KEY (metric_date, category_name, priority)
);

CREATE INDEX idx_tickets_opened       ON tickets(opened_at);
CREATE INDEX idx_tickets_category     ON tickets(category_id);
CREATE INDEX idx_tickets_user         ON tickets(reporter_user_id);
CREATE INDEX idx_tickets_asset        ON tickets(asset_tag);
CREATE INDEX idx_keywords_keyword     ON ticket_keywords(keyword);

CREATE VIEW v_ticket_full AS
SELECT
    t.ticket_id,
    t.opened_at,
    t.closed_at,
    t.status,
    t.priority,
    t.resolution_hours,
    t.sla_breached,
    t.short_description,
    t.resolution_notes,
    c.category_name,
    u.full_name           AS reporter_name,
    u.email               AS reporter_email,
    d.dept_id,
    d.dept_name,
    d.location,
    a.asset_id,
    a.asset_tag,
    a.model               AS asset_model,
    a.asset_type,
    a.compliance_status,
    a.age_years
FROM tickets t
LEFT JOIN ticket_categories c ON c.category_id = t.category_id
LEFT JOIN users u             ON u.user_id     = t.reporter_user_id
LEFT JOIN departments d       ON d.dept_id     = u.dept_id
LEFT JOIN assets a            ON a.asset_tag   = t.asset_tag;
