import sqlite3

DB_NAME = "threat_intel.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Membuat tabel jika belum ada."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            summary TEXT,
            source TEXT,
            published_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vuln_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cve_id TEXT UNIQUE,
            description TEXT,
            cvss_score REAL,
            severity TEXT,
            first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabel Relasi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_vuln_events (
            article_id INTEGER,
            event_id INTEGER,
            PRIMARY KEY (article_id, event_id),
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (event_id) REFERENCES vuln_events(id)
        )
    """)

    conn.commit()
    conn.close()

def save_to_db(news_item: dict, cves: list[str], source: str) -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO articles (url, title, summary, source, published_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        news_item.get("link"), news_item.get("title"), news_item.get("summary"),
        source, news_item.get("published")
    ))

    cursor.execute("SELECT id FROM articles WHERE url = ?", (news_item.get("link"),))
    article_id = cursor.fetchone()[0]

    new_cves_found = []

    for cve in cves:
        cursor.execute("SELECT id FROM vuln_events WHERE cve_id = ?", (cve,))
        row = cursor.fetchone()

        if row:
            event_id = row[0]
        else:
            cursor.execute("INSERT INTO vuln_events (cve_id) VALUES (?)", (cve,))
            event_id = cursor.lastrowid
            new_cves_found.append(cve)

        cursor.execute("""
            INSERT OR IGNORE INTO article_vuln_events (article_id, event_id)
            VALUES (?, ?)
        """, (article_id, event_id))

    conn.commit()
    conn.close()

    return new_cves_found

def get_unenriched_cves():
    """Ambil CVE yang belum punya detail (description masih NULL)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cve_id FROM vuln_events
        WHERE description IS NULL LIMIT 10
    """)
    cves = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cves

def save_enrichment(cve_id: str, data: dict):
    """Simpan detail CVE yang didapat dari vulnx ke database."""
    conn = get_connection()
    cursor = conn.cursor()

    description = data.get("description") or data.get("summary") or "No description available"

    cvss_raw = data.get("cvss_score") or data.get("cvss") or 0.0
    try:
        cvss_score = float(cvss_raw)
    except (ValueError, TypeError):
        cvss_score = 0.0

    severity = data.get("severity") or "unknown"

    cursor.execute("""
        UPDATE vuln_events
        SET description = ?, cvss_score = ?, severity = ?
        WHERE cve_id = ?
    """, (description, cvss_score, severity, cve_id))

    conn.commit()
    conn.close()
