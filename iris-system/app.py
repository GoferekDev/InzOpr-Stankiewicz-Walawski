import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = 'app.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        # Włączenie kluczy obcych w SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Tworzenie tabel zgodnych z mapą v1
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS klient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imie TEXT,
                nazwisko TEXT,
                telefon TEXT,
                email TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formularz_zgloszenia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opis_problemu TEXT,
                data_zgloszenia DATETIME DEFAULT CURRENT_TIMESTAMP,
                klient_id INTEGER,
                FOREIGN KEY (klient_id) REFERENCES klient(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urzadzenie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                typ_sprzetu TEXT,
                model TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kategoria_uslugi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT
            )
        ''')
        cursor.execute('''
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
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anulowanie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                powod TEXT,
                zlecenie_id INTEGER UNIQUE,
                FOREIGN KEY (zlecenie_id) REFERENCES zlecenie(id)
            )
        ''')

        # Wprowadzenie danych początkowych (kategorie usług)
        cursor.execute("SELECT COUNT(*) FROM kategoria_uslugi")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (1, 'Serwisowe')")
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (2, 'Utrzymywanie urządzeń')")
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (3, 'Odzyskiwanie danych')")

        db.commit()

# --- WIDOKI (W01 - W05) ---

@app.route('/', methods=['GET', 'POST'])
def w01_index():
    """W01: Strona Główna z Weryfikacją Statusu"""
    if request.method == 'POST':
        numer = request.form.get('numer', '').strip()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM zlecenie WHERE numer = ?", (numer,))
        zlecenie = cursor.fetchone()
        if zlecenie:
            return redirect(url_for('w04_status', numer=numer))
        else:
            return render_template('w01_index.html', error="Nieprawidłowy numer zlecenia")
    return render_template('w01_index.html')

@app.route('/zgloszenie', methods=['GET', 'POST'])
def w02_form():
    """W02: Formularz Zgłoszeniowy Online"""
    if request.method == 'POST':
        imie = request.form.get('imie')
        nazwisko = request.form.get('nazwisko')
        telefon = request.form.get('telefon')
        email = request.form.get('email')
        typ_sprzetu = request.form.get('typ_sprzetu')
        model = request.form.get('model')
        kategoria_id = request.form.get('kategoria_id')
        opis = request.form.get('opis')

        if not all([imie, email, typ_sprzetu, model, opis]):
            return render_template('w02_form.html', error="Wypełnij wszystkie wymagane pola.")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Zapis klienta
        cursor.execute("INSERT INTO klient (imie, nazwisko, telefon, email) VALUES (?, ?, ?, ?)",
                       (imie, nazwisko, telefon, email))
        klient_id = cursor.lastrowid

        # Zapis formularza
        cursor.execute("INSERT INTO formularz_zgloszenia (opis_problemu, klient_id) VALUES (?, ?)",
                       (opis, klient_id))
        formularz_id = cursor.lastrowid

        # Zapis urządzenia
        cursor.execute("INSERT INTO urzadzenie (typ_sprzetu, model) VALUES (?, ?)",
                       (typ_sprzetu, model))
        urzadzenie_id = cursor.lastrowid

        # Generowanie unikalnego numeru zlecenia (np. IRIS-7892)
        numer_zlecenia = "IRIS-" + ''.join(random.choices(string.digits, k=4))

        # Zapis zlecenia
        cursor.execute("""
            INSERT INTO zlecenie (numer, status, formularz_id, urzadzenie_id, kategoria_id)
            VALUES (?, 'NEW', ?, ?, ?)
        """, (numer_zlecenia, formularz_id, urzadzenie_id, kategoria_id))

        db.commit()
        return redirect(url_for('w03_success', numer=numer_zlecenia))

    return render_template('w02_form.html')

@app.route('/sukces/<numer>')
def w03_success(numer):
    """W03: Potwierdzenie Zgłoszenia"""
    return render_template('w03_success.html', numer=numer)

@app.route('/status/<numer>', methods=['GET', 'POST'])
def w04_status(numer):
    """W04: Status Zlecenia i Anulowanie"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT z.*, u.typ_sprzetu, u.model, k.imie, k.email
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        WHERE z.numer = ?
    """, (numer,))
    zlecenie = cursor.fetchone()

    if not zlecenie:
        return render_template('w01_index.html', error="Nie znaleziono zlecenia.")

    if request.method == 'POST':
        if zlecenie['status'] == 'NEW':
            cursor.execute("UPDATE zlecenie SET status = 'CANCELLED' WHERE numer = ?", (numer,))
            cursor.execute("INSERT INTO anulowanie (powod, zlecenie_id) VALUES ('Anulowane przez klienta online', ?)", (zlecenie['id'],))
            db.commit()
            return redirect(url_for('w04_status', numer=numer))
        else:
            error_msg = "Nie można anulować zlecenia. Sprzęt został już dostarczony do serwisu."
            return render_template('w04_status.html', zlecenie=zlecenie, error=error_msg)

    return render_template('w04_status.html', zlecenie=zlecenie)

@app.route('/panel-technika', methods=['GET', 'POST'])
def w05_tech():
    """W05: Panel Technika – Przyjęcie Sprzętu"""
    db = get_db()
    cursor = db.cursor()

    message = None
    if request.method == 'POST':
        numer = request.form.get('numer', '').strip()
        cursor.execute("SELECT * FROM zlecenie WHERE numer = ?", (numer,))
        zlecenie = cursor.fetchone()

        if zlecenie:
            if zlecenie['status'] == 'NEW':
                cursor.execute("UPDATE zlecenie SET status = 'DELIVERED' WHERE numer = ?", (numer,))
                db.commit()
                message = f"Zlecenie {numer} zostało przyjęte (status zmieniony na DELIVERED)."
            else:
                message = f"Zlecenie ma już status: {zlecenie['status']}."
        else:
            message = "Nie znaleziono zlecenia o takim numerze."

    # Poprawione zapytanie SQL (zamieniono nazwiskootc na nazwisko)
    cursor.execute("""
        SELECT z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwisko AS nazwisko
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
    """)
    zlecenia = cursor.fetchall()

    return render_template('w05_tech.html', zlecenia=zlecenia, message=message)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
