# db_sqlite.py

import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "news_agent.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        source_name    TEXT,
        source_url     TEXT,
        article_url    TEXT,

        title          TEXT,
        content        TEXT,
        snippet        TEXT,

        industry       TEXT,

        published_at   TEXT,
        content_hash   TEXT UNIQUE,

        created_at     TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT,
        article_url  TEXT,
        created_at   TEXT DEFAULT (datetime('now')),
        is_completed  INTEGER DEFAULT 0
    );
    """)

    conn.commit()
    conn.close()


def insert_article(article: dict, category: str) -> str:
	"""
	Inserts article into DB.
	Returns: 'saved' or 'duplicate'
	"""
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()

	content_hash = hashlib.sha256(
		article["text"].encode()
	).hexdigest()

	cur.execute("""
	INSERT OR IGNORE INTO raw_messages
	(source_name, source_url, article_url, title, content,
	 snippet, industry, published_at, content_hash, created_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	""", (
		article.get("source"),
		article.get("url"),
		article.get("title"),
		article.get("text"),
		article.get("text")[:500],
		category,
		article.get("publish_date"),
		content_hash,
		datetime.now().isoformat()
	))

	conn.commit()

	if cur.rowcount == 0:
		status = "duplicate"
	else:
		status = "saved"

	conn.close()
	return status


def insert_article_from_dict(article: dict) -> str:
	"""
	Inserts article into raw_messages table from a dictionary.
	Input dictionary should have keys: source_name, source_url, article_url, title,
	content, snippet, industry, published_at, content_hash, created_at
	Returns: 'saved' or 'duplicate'
	"""
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()

	try:
		cur.execute("""
		INSERT OR IGNORE INTO raw_messages
		(source_name, source_url, article_url, title, content,
		 snippet, industry, published_at, content_hash, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""", (
			article.get("source_name"),
			article.get("source_url"),
			article.get("article_url"),
			article.get("title"),
			article.get("content"),
			article.get("snippet"),
			article.get("industry"),
			article.get("published_at"),
			str(article.get("content_hash")),
			article.get("created_at")
		))

		conn.commit()

		if cur.rowcount == 0:
			status = "duplicate"
		else:
			status = "saved"

	except Exception as e:
		print(f"Error inserting article: {e}")
		status = "error"
	finally:
		conn.close()



def insert_raw_link(title: str, article_url: str) -> None:
    """
    Inserts a link into the raw_links table.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO raw_links (title, article_url,is_completed)
        VALUES (?, ?, ?)
        """,
        (title, article_url, 0)
    )
    conn.commit()
    conn.close()


def get_all_raw_links() -> list:
	"""
	Retrieves all rows from the raw_links table.
	Returns: List of tuples containing (id, title, article_url, created_at, is_completed)
	"""
	conn = sqlite3.connect(DB_FILE)
	cur = conn.cursor()
	
	try:
		cur.execute("SELECT * FROM raw_links")
		rows = cur.fetchall()
		return rows
	except Exception as e:
		print(f"Error retrieving raw_links: {e}")
		return []
	finally:
		conn.close()

init_db()