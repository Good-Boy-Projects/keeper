import sqlite3

def get_db():
    conn = sqlite3.connect("keeper.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_bookmarks(folder=None, tag=None):
    db = get_db()
    query = """
        SELECT b.*,
               GROUP_CONCAT(DISTINCT f.name) as folders,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM bookmarks b
        LEFT JOIN bookmark_folders bf ON b.id = bf.bookmark_id
        LEFT JOIN folders f           ON bf.folder_id = f.id
        LEFT JOIN bookmark_tags bt    ON b.id = bt.bookmark_id
        LEFT JOIN tags t              ON bt.tag_id = t.id
        WHERE b.is_archived = 0
    """
    params = []
    if folder:
        query += " AND f.name = ?"
        params.append(folder)
    if tag:
        query += " AND t.name = ?"
        params.append(tag)
    query += " GROUP BY b.id ORDER BY b.saved_at DESC"
    return db.execute(query, params).fetchall()

def get_bookmark(id):
    db = get_db()
    return db.execute("""
        SELECT b.*,
               GROUP_CONCAT(DISTINCT f.name) as folders,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM bookmarks b
        LEFT JOIN bookmark_folders bf ON b.id = bf.bookmark_id
        LEFT JOIN folders f           ON bf.folder_id = f.id
        LEFT JOIN bookmark_tags bt    ON b.id = bt.bookmark_id
        LEFT JOIN tags t              ON bt.tag_id = t.id
        WHERE b.id = ?
        GROUP BY b.id
    """, (id,)).fetchone()

def create_bookmark(data):
    db = get_db()
    cursor = db.execute("""
        INSERT INTO bookmarks (
            url, title, description, author, content,
            image_url, favicon_url, domain, published,
            word_count, site_name, language, read_time,
            canonical_url, article_path
        ) VALUES (
            :url, :title, :description, :author, :content,
            :image_url, :favicon_url, :domain, :published,
            :word_count, :site_name, :language, :read_time,
            :canonical_url, :article_path
        )
    """, data)
    db.commit()
    return cursor.lastrowid

def update_bookmark(id, data):
    db = get_db()
    db.execute("""
        UPDATE bookmarks
        SET title = :title
        WHERE id = :id
    """, {"title": data["title"], "id": id})

    db.execute("DELETE FROM bookmark_folders WHERE bookmark_id = ?", (id,))
    for folder_name in data.get("folders", []):
        folder = db.execute(
            "SELECT id FROM folders WHERE name = ?", (folder_name,)
        ).fetchone()
        if folder:
            db.execute(
                "INSERT INTO bookmark_folders (bookmark_id, folder_id) VALUES (?, ?)",
                (id, folder["id"])
            )

    db.execute("DELETE FROM bookmark_tags WHERE bookmark_id = ?", (id,))
    for tag_name in data.get("tags", []):
        tag = db.execute(
            "SELECT id FROM tags WHERE name = ?", (tag_name,)
        ).fetchone()
        if tag:
            db.execute(
                "INSERT INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
                (id, tag["id"])
            )

    db.commit()

from files import delete_article

def delete_bookmark(id):
    db = get_db()
    bookmark = get_bookmark(id)
    if bookmark and bookmark["article_path"]:
        delete_article(bookmark["article_path"])
    db.execute("DELETE FROM bookmarks WHERE id = ?", (id,))
    db.commit()

def toggle_favorite(id):
    db = get_db()
    db.execute(
        "UPDATE bookmarks SET is_favorite = 1 - is_favorite WHERE id = ?",
        (id,)
    )
    db.commit()

def toggle_archive(id):
    db = get_db()
    db.execute(
        "UPDATE bookmarks SET is_archived = 1 - is_archived WHERE id = ?",
        (id,)
    )
    db.commit()

def get_all_folders():
    db = get_db()
    return db.execute("SELECT * FROM folders ORDER BY name ASC").fetchall()

def get_all_tags():
    db = get_db()
    return db.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()

def get_favorites():
    db = get_db()
    return db.execute("""
        SELECT b.*,
               GROUP_CONCAT(DISTINCT f.name) as folders,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM bookmarks b
        LEFT JOIN bookmark_folders bf ON b.id = bf.bookmark_id
        LEFT JOIN folders f           ON bf.folder_id = f.id
        LEFT JOIN bookmark_tags bt    ON b.id = bt.bookmark_id
        LEFT JOIN tags t              ON bt.tag_id = t.id
        WHERE b.is_favorite = 1
        GROUP BY b.id
        ORDER BY b.saved_at DESC
    """).fetchall()

def get_archived():
    db = get_db()
    return db.execute("""
        SELECT b.*,
               GROUP_CONCAT(DISTINCT f.name) as folders,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM bookmarks b
        LEFT JOIN bookmark_folders bf ON b.id = bf.bookmark_id
        LEFT JOIN folders f           ON bf.folder_id = f.id
        LEFT JOIN bookmark_tags bt    ON b.id = bt.bookmark_id
        LEFT JOIN tags t              ON bt.tag_id = t.id
        WHERE b.is_archived = 1
        GROUP BY b.id
        ORDER BY b.saved_at DESC
    """).fetchall()

def get_untagged():
    db = get_db()
    return db.execute("""
        SELECT b.*,
               GROUP_CONCAT(DISTINCT f.name) as folders,
               GROUP_CONCAT(DISTINCT t.name) as tags
        FROM bookmarks b
        LEFT JOIN bookmark_folders bf ON b.id = bf.bookmark_id
        LEFT JOIN folders f           ON bf.folder_id = f.id
        LEFT JOIN bookmark_tags bt    ON b.id = bt.bookmark_id
        LEFT JOIN tags t              ON bt.tag_id = t.id
        WHERE b.id NOT IN (SELECT bookmark_id FROM bookmark_tags)
        GROUP BY b.id
        ORDER BY b.saved_at DESC
    """).fetchall()