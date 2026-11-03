0. Wybór Technologii

Model: Gemini

Prompt:
- Jakie technologie polecasz do realizacji tego projektu?
Odpowiedź Modelu:
Na podstawie wytycznych do **Laboratorium 03 (Technologie i prompty AI)** oraz specyfiki Waszego projektu **Iris Solutions (System Zarządzania Zleceniami Usług IT)**, rekomenduję sprawdzony, lekki i całkowicie bezpłatny zestaw technologii do lokalnego uruchomienia wersji **v1**.

---

## Rekomendowany zestaw technologii dla *Iris Solutions* (v1)

| Obszar | Wybrana technologia | Rola w projekcie *Iris Solutions* |
| --- | --- | --- |
| **Widoki (Frontend)** | HTML, CSS, JavaScript | Odpowiadają za treść, wygląd oraz obsługę formularzy (strona główna, formularz zgłoszeniowy usterki, panel weryfikacji statusu oraz panel technika).

 |
| **Serwer (Backend)** | Python 3 + Flask | Obsługuje żądania HTTP, trasowanie (routing), walidację wprowadzanych przez użytkowników danych oraz kluczowe reguły biznesowe systemu.

 |
| **Baza danych** | SQLite (moduł `sqlite3`) | Zapewnia trwały zapis danych w lokalnym pliku (tabeli klientów, urządzeń, zleceń i statusów) bez konieczności stawiania zewnętrznych serwerów bazodanowych.

 |
| **Praca zespołowa** | Edytor kodu (np. VS Code), Git, GitHub | Służą do wspólnej edycji kodu źródłowego, kontroli wersji oraz weryfikacji wkładu obu osób w zespole.

 |

---

## Uzasadnienie wyboru (do zapisu w pliku `docs/technologie.md`)

Zestaw oparty na języku Python, lekkim frameworku Flask oraz wbudowanej bazie SQLite jest idealnym wyborem dla dwuosobowego zespołu do realizacji projektu inżynierskiego. Flask pozwala na błyskawiczne uruchomienie serwera aplikacji i jest bardzo elastyczny w pisaniu logiki procesów biznesowych (takich jak walidacja zgłoszeń czy zmiana stanów zleceń). SQLite nie wymaga skomplikowanej instalacji ani konfiguracji serwerów – cała baza danych zapisanego systemu znajduje się w jednym lokalnym pliku, co drastycznie ułatwia uruchomienie projektu i testowanie go przez obie osoby na własnych komputerach. Standardowe technologie webowe (HTML/CSS/JS) gwarantują pełną zgodność z przygotowanymi wcześniej szkicami interfejsu (wireframe'ami). Ponadto całe środowisko jest w pełni darmowe, nie wymaga płatnych subskrypcji ani zewnętrznych kluczy API, a modele sztucznej inteligencji radzą sobie perfekcyjnie z generowaniem i debugowaniem kodu w tym stosie.


1. Szkielet
Model: Gemini

Prompt:
Przygotuj szkielet Iris v1: HTML/CSS, Python 3, Flask i SQLite
Plik startowy: app.py.

Widoki z cyklu pierwszego: W01,W02,W03,W04,W05

 Zwróć strukturę katalogów, pełną zawartość plików,
requirements.txt i instrukcję startu. Dodaj .gitignore dla .venv i lokalnej bazy. Podaj prosty sposób
sprawdzenia każdego widoku. Zachowaj zakres v1

Oto kompletny szkielet aplikacji **Iris Solutions v1** oparty na technologiach Python 3, Flask, SQLite oraz HTML/CSS, przygotowany zgodnie z wytycznymi z laboratorium.

---

## 1. Struktura katalogów projektu

```text
iris-system/
│
├── .venv/                  # Środowisko wirtualne Pythona (pomijane przez Git)
├── app.db                  # Lokalna baza danych SQLite (tworzona automatycznie)
├── requirements.txt        # Zależności projektu
├── .gitignore              # Pliki ignorowane przez Git
└── templates/              # Szablony HTML widoków
    ├── w01_index.html      # W01: Strona Główna / Weryfikacja Statusu
    ├── w02_form.html       # W02: Formularz Zgłoszeniowy Online
    ├── w03_success.html    # W03: Potwierdzenie Zgłoszenia
    ├── w04_status.html     # W04: Status Zlecenia i Anulowanie
    └── w05_tech.html       # W05: Panel Technika (Przyjęcie sprzętu)

```

---

## 2. Zawartość plików

### `.gitignore`

```text
.venv/
__pycache__/
*.pyc
app.db
instance/

```

### `requirements.txt`

```text
Flask==3.0.2

```

### `app.py`

```python
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

    # Pobierz listę aktywnych zleceń do podglądu w panelu
    cursor.execute("""
        SELECT z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwiskootc AS nazwisko 
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

```

---

### Szablony HTML (`templates/`)

#### `templates/w01_index.html`

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Iris Solutions - Strona Główna</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .error { color: red; margin-bottom: 15px; }
        input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
        button { background: #000; color: #fff; border: none; cursor: pointer; }
        button:hover { background: #333; }
    </style>
</head>
<body>
<div class="container">
    <h2>Zakład IT - Iris Solutions</h2>
    <p>Szybkie naprawy w przystępnej cenie</p>
    
    <hr>
    <h3>Sprawdź status zamówienia</h3>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>ID Zlecenia (np. IRIS-1234):</label>
        <input type="text" name="numer" required>
        <button type="submit">Sprawdź</button>
    </form>

    <br>
    <a href="{{ url_for('w02_form') }}"><button style="background: #0056b3;">Zgłoś usterkę (Nowe Zlecenie)</button></a>
    <br><br>
    <a href="{{ url_for('w05_tech') }}">Przejdź do Panelu Technika (W05)</a>
</div>
</body>
</html>

```

#### `templates/w02_form.html`

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Formularz Zgłoszeniowy - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input, select, textarea, button { padding: 8px; margin: 5px 0 15px 0; width: 100%; box-sizing: border-box; }
        .error { color: red; margin-bottom: 15px; }
        button { background: #28a745; color: white; border: none; cursor: pointer; padding: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h2>Formularz Zgłoszeniowy Usterki</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <label>Imię:</label>
        <input type="text" name="imie" required>
        
        <label>Nazwisko:</label>
        <input type="text" name="nazwisko">
        
        <label>Telefon:</label>
        <input type="text" name="telefon">
        
        <label>E-mail:</label>
        <input type="email" name="email" required>
        
        <label>Typ urządzenia (np. Laptop, Smartfon):</label>
        <input type="text" name="typ_sprzetu" required>
        
        <label>Producent i model:</label>
        <input type="text" name="model" required>
        
        <label>Kategoria usługi:</label>
        <select name="kategoria_id">
            <option value="1">Serwisowe</option>
            <option value="2">Utrzymywanie urządzeń</option>
            <option value="3">Odzyskiwanie danych</option>
        </select>
        
        <label>Opis problemu:</label>
        <textarea name="opis" rows="4" required></textarea>
        
        <button type="submit">Wyślij zgłoszenie</button>
    </form>
    <br>
    <a href="{{ url_for('w01_index') }}">Powrót do strony głównej</a>
</div>
</body>
</html>

```

#### `templates/w03_success.html`

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Potwierdzenie - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: #ffe6e6; border: 2px solid #ff4d4d; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; text-align: center; }
        .code { font-size: 24px; font-weight: bold; color: #d9534f; margin: 15px 0; }
    </style>
</head>
<body>
<div class="container">
    <h2>DZIĘKUJEMY ZA ZLECENIE</h2>
    <p>Twój numer zlecenia potrzebny do sprawdzania statusu:</p>
    <div class="code">{{ numer }}</div>
    <p>Zapisz ten numer. Wskazówki i potwierdzenie otrzymasz również mailem.</p>
    <br>
    <a href="{{ url_for('w01_index') }}">Sprawdź status zamówienia</a>
</div>
</body>
</html>

```

#### `templates/w04_status.html`

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Status Zlecenia - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .box { border: 1px solid #ccc; padding: 15px; margin: 15px 0; background: #fafafa; }
        .error { color: red; margin-bottom: 15px; }
        button.cancel { background: #dc3545; color: white; border: none; padding: 10px; cursor: pointer; width: 100%; }
    </style>
</head>
<body>
<div class="container">
    <h2>Wynik Wyszukiwania Statusu</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    
    <div class="box">
        <p><strong>Zlecenie NR:</strong> {{ zlecenie.numer }}</p>
        <p><strong>Urządzenie:</strong> {{ zlecenie.typ_sprzetu }} - {{ zlecenie.model }}</p>
        <p><strong>Klient:</strong> {{ zlecenie.imie }} ({{ zlecenie.email }})</p>
        <p><strong>Aktualny Status:</strong> <span style="color: #007bff; font-weight: bold;">{{ zlecenie.status }}</span></p>
    </div>

    {% if zlecenie.status == 'NEW' %}
    <form method="POST">
        <button type="submit" class="cancel">Anuluj Zamówienie</button>
    </form>
    {% elif zlecenie.status == 'DELIVERED' %}
    <p style="color: gray;"><em>Sprzęt został dostarczony do serwisu. Anulowanie online nie jest już możliwe.</em></p>
    {% elif zlecenie.status == 'CANCELLED' %}
    <p style="color: red;"><em>To zlecenie zostało anulowane.</em></p>
    {% endif %}

    <br>
    <a href="{{ url_for('w01_index') }}">Powrót do strony głównej</a>
</div>
</body>
</html>

```

#### `templates/w05_tech.html`

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Panel Technika - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 800px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #333; color: white; }
        .msg { background: #e2f0d9; padding: 10px; margin-bottom: 15px; border: 1px solid #c8e1b9; }
        input, button { padding: 8px; margin: 5px 0; }
        button { background: #17a2b8; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
<div class="container">
    <h2>Panel Technika – Przyjęcie Sprzętu</h2>
    
    {% if message %}<div class="msg">{{ message }}</div>{% endif %}

    <form method="POST">
        <label>Podaj ID / Numer zlecenia od klienta:</label><br>
        <input type="text" name="numer" placeholder="np. IRIS-1234" required>
        <button type="submit">Potwierdź przyjęcie sprzętu (Zmień na DELIVERED)</button>
    </form>

    <hr style="margin: 20px 0;">

    <h3>Lista wszystkich zleceń w systemie:</h3>
    <table>
        <tr>
            <th>Numer</th>
            <th>Klient</th>
            <th>Urządzenie</th>
            <th>Status</th>
        </tr>
        {% for z in zlecenia %}
        <tr>
            <td>{{ z.numer }}</td>
            <td>{{ z.imie }}</td>
            <td>{{ z.typ_sprzetu }} - {{ z.model }}</td>
            <td><strong>{{ z.status }}</strong></td>
        </tr>
        {% endfor %}
    </table>

    <br>
    <a href="{{ url_for('w01_index') }}">Powrót do strony głównej</a>
</div>
</body>
</html>

```

---

## 3. Instrukcja startu (Windows PowerShell / macOS / Linux)

Otwórz terminal w folderze projektu (`iris-system/`) i wykonaj polecenia odpowiednie dla swojego systemu:

### **Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py

```

### **macOS / Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py

```

Po uruchomieniu serwera w terminalu otworzy się lokalny adres: **`[http://127.0.0.1:5000](http://127.0.0.1:5000)`**.

---

## 4. Sposób sprawdzenia każdego widoku (Scenariusze testowe v1)

1. **W01 (Strona Główna / Weryfikacja Statusu):**
* Wejdź na `[http://127.0.0.1:5000/](http://127.0.0.1:5000/)`. Wpisz losowy ciąg znaków w pole ID zlecenia i kliknij *Sprawdź* – upewnij się, że pojawi się komunikat o błędzie *„Nieprawidłowy numer zlecenia”*.




2. **W02 (Formularz Zgłoszeniowy):**
* Kliknij *Zgłoś usterkę*. Wypełnij formularz danymi testowymi (np. Jan Kowalski, jan@example.com, Laptop, Dell, opis usterki) i wyślij.


3. **W03 (Potwierdzenie Zgłoszenia):**
* Po wysłaniu formularza zostaniesz przekierowany do widoku W03, gdzie zobaczysz wygenerowany unikalny numer zlecenia (np. `IRIS-4819`). Skopiuj ten numer.


4. **W04 (Status Zlecenia i Anulowanie):**
* Wróć na stronę główną, wklej skopiowany numer zlecenia i kliknij *Sprawdź*. Zobaczysz szczegóły oraz status `NEW`. Możesz kliknąć przycisk *Anuluj Zamówienie* (status zmieni się na `CANCELLED`).


5. **W05 (Panel Technika):**
* Utwórz nowe zgłoszenie, aby miało status `NEW`. Następnie przejdź pod adres `[http://127.0.0.1:5000/panel-technika](http://127.0.0.1:5000/panel-technika)`. Wpisz numer nowego zlecenia i zatwierdź – status w bazie i tabeli zmieni się na `DELIVERED`, a ponowna próba anulowania tego zlecenia przez klienta w W04 zostanie zablokowana.

---
Co zrobić w kolejnych wersjach?
Naprawa wizualna widoków. Rozszerzenie funkcjonalności
