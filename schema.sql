-- Core tables created first - bookmarks, folders, and tags

CREATE TABLE IF NOT EXISTS bookmarks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    url           TEXT NOT NULL,
    title         TEXT,
    description   TEXT,
    author        TEXT,
    content       TEXT,
    image_url     TEXT,
    favicon_url   TEXT,
    domain        TEXT,
    published     TEXT,
    saved_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_favorite   INTEGER DEFAULT 0,
    is_archived   INTEGER DEFAULT 0,
    word_count    INTEGER DEFAULT 0,
    site_name     TEXT,
    language      TEXT,
    read_time     INTEGER,
    canonical_url TEXT
);

CREATE TABLE IF NOT EXISTS folders (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- These tables get joined, since they reference the tables created above

CREATE TABLE IF NOT EXISTS bookmark_folders (
    bookmark_id INTEGER REFERENCES bookmarks(id) ON DELETE CASCADE,
    folder_id   INTEGER REFERENCES folders(id)   ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, folder_id)
);

CREATE TABLE IF NOT EXISTS bookmark_tags (
    bookmark_id INTEGER REFERENCES bookmarks(id) ON DELETE CASCADE,
    tag_id      INTEGER REFERENCES tags(id)       ON DELETE CASCADE,
    PRIMARY KEY (bookmark_id, tag_id)
);
