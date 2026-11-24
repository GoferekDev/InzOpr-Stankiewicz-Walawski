import os
import sqlite3
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "app.db")


def get_db(db_path=DEFAULT_DB_PATH):
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
    return db


def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS klient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imie TEXT,
                nazwisko TEXT,
                telefon TEXT,
                email TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS formularz_zgloszenia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opis_problemu TEXT,
                data_zgloszenia DATETIME DEFAULT CURRENT_TIMESTAMP,
                klient_id INTEGER,
                FOREIGN KEY (klient_id) REFERENCES klient(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urzadzenie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                typ_sprzetu TEXT,
                model TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kategoria_uslugi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zlecenie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numer TEXT UNIQUE,
                data_utworzenia DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'NEW',
                formularz_id INTEGER,
                urzadzenie_id INTEGER,
                kategoria_id INTEGER,
                FOREIGN KEY (formularz_id) REFERENCES formularz_zgloszenia(id),
                FOREIGN KEY (urzadzenie_id) REFERENCES urzadzenie(id),
                FOREIGN KEY (kategoria_id) REFERENCES kategoria_uslugi(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anulowanie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                powod TEXT,
                zlecenie_id INTEGER UNIQUE,
                FOREIGN KEY (zlecenie_id) REFERENCES zlecenie(id)
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM kategoria_uslugi")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO kategoria_uslugi (id, nazwa) VALUES (?, ?)",
                [
                    (1, "Serwisowe"),
                    (2, "Utrzymywanie urządzeń"),
                    (3, "Odzyskiwanie danych"),
                ],
            )

        conn.commit()
    finally:
        conn.close()
