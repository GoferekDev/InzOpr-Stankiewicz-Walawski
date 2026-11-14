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


2. Cykl 2
Model: Gemini

Prompt: Uzupełnij ten projekt o funkcjonalność z Cyklu 2, zawartego w pliku roadmap-v1.md. Projekt jest tworzony z zastosowaniem technologii Python 3, Flask, SQLite, HTML, CSS i Javascript . 

Poniżej znajduje się kompletna rozbudowa aplikacji **Iris Solutions** o funkcjonalności **Cyklu 2** zgodnie z dokumentem `roadmap-v1.md` oraz specyfikacją UML zawartą w `Dokumentacjav1.2.docx`.

### Podsumowanie zmian w ramach Cyklu 2

1. **Baza danych (`init_db`)**: Dodano tabele `technik` (B07), `kosztorys` (B08), `naprawa` (B09), `czesc` (B10) oraz `zlecenie_czesc` (B11), wraz z danymi startowymi (przykładowi technicy oraz asortyment magazynu, w tym pozycje ze stanem `0` do przetestowania automatycznego zamawiania).


2. **Moduł integracyjny z hurtownią (`WarehouseApiClient`)**: Zaimplementowano klasę symulującą komunikację z zewnętrznym API hurtowni (z obsługą błędu transmisji zgodnie ze specyfikacją F07 oraz możliwością ponowienia próby).


3. **Rozszerzone widoki i trasy**:
* **`W04` (`w04_status.html`)**: Wyświetlanie diagnozy, kosztorysu oraz formularz akceptacji (`AKCEPTOWANY`) lub odrzucenia (`ODRZUCONY` -> zmiana statusu zlecenia na `COMPLETED`) zgodnie z **F06**.


* **`W05` (`w05_tech.html`)**: Zaktualizowana lista zleceń z nawigacją do diagnozy (`W06`) oraz części (`W07`), a także możliwością oznaczenia naprawy jako zakończonej (`COMPLETED`).


* **`W06` (`w06_diagnoza.html`)**: Panel wprowadzania opisu diagnozy, szacowanego czasu naprawy i kwoty kosztorysu (`DELIVERED` -> `IN_PROGRESS`, utworzenie rekordu w `kosztorys` ze statusem `OCZEKUJE`) zgodnie z **F05**.


* **`W07` (`w07_czesci.html`)**: Przypisywanie części do zlecenia (wymagany zaakceptowany kosztorys), sprawdzanie stanów magazynowych, automatyczne zamawianie brakujących komponentów przez `WarehouseApiClient` (`WAITING_FOR_PARTS`), ponawianie nieudanych transmisji oraz rejestrowanie dostawy części z hurtowni (`DOSTARCZONE` -> powrót statusu zlecenia do `IN_PROGRESS`) zgodnie z **F07** i Scenariuszem 7.





---

### 1. Zaktualizowany plik `app.py`

> **Uwaga:** Przed pierwszym uruchomieniem po aktualizacji usuń stary plik `app.db` (lub pozwól funkcji `init_db()` utworzyć brakujące tabele – wszystkie nowe tabele posiadają klauzulę `CREATE TABLE IF NOT EXISTS`, więc zachowają też dotychczasowe dane z Cyklu 1).

```python
import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = 'app.db'


# --- KLASA INTEGRACJI Z HURTOWNIĄ (WarehouseApiClient - wg specyfikacji UML) ---
class WarehouseApiClient:
    """Symuluje komunikację z zewnętrznym API hurtowni."""

    @staticmethod
    def send_order(zlecenie_numer: str, czesc_id: int, czesc_nazwa: str, ilosc: int, simulate_error: bool = False) -> tuple[bool, str]:
        if simulate_error:
            return False, f"Błąd połączenia z API hurtowni podczas zamawiania: {czesc_nazwa} (zlecenie {zlecenie_numer})."
        # Symulacja poprawnej odpowiedzi API hurtowni
        external_order_id = "HURT-" + ''.join(random.choices(string.digits, k=5))
        return True, f"Zamówienie {external_order_id} na {ilosc} szt. '{czesc_nazwa}' zostało przyjęte przez hurtownię."


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
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- TABELE CYKL 1 ---
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

        # --- TABELE CYKL 2 (B07 - B11) ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technik (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                imie TEXT,
                nazwisko TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kosztorys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kwota DECIMAL(10, 2),
                status_akceptacji TEXT DEFAULT 'OCZEKUJE',
                zlecenie_id INTEGER UNIQUE,
                FOREIGN KEY (zlecenie_id) REFERENCES zlecenie(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS naprawa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opis TEXT,
                czas_naprawy INTEGER,
                zlecenie_id INTEGER UNIQUE,
                technik_id INTEGER,
                FOREIGN KEY (zlecenie_id) REFERENCES zlecenie(id),
                FOREIGN KEY (technik_id) REFERENCES technik(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS czesc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT,
                cena DECIMAL(10, 2),
                dostepnosc INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zlecenie_czesc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zlecenie_id INTEGER,
                czesc_id INTEGER,
                ilosc INTEGER,
                status_zamowienia TEXT,
                FOREIGN KEY (zlecenie_id) REFERENCES zlecenie(id),
                FOREIGN KEY (czesc_id) REFERENCES czesc(id)
            )
        ''')

        # Dane początkowe: kategorie usług
        cursor.execute("SELECT COUNT(*) FROM kategoria_uslugi")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (1, 'Serwisowe')")
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (2, 'Utrzymywanie urządzeń')")
            cursor.execute("INSERT INTO kategoria_uslugi (id, nazwa) VALUES (3, 'Odzyskiwanie danych')")

        # Dane początkowe: technicy (B07)
        cursor.execute("SELECT COUNT(*) FROM technik")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO technik (imie, nazwisko) VALUES ('Jan', 'Kowalski')")
            cursor.execute("INSERT INTO technik (imie, nazwisko) VALUES ('Anna', 'Nowak')")

        # Dane początkowe: magazyn części (B10) - z różną dostępnością do testów F07
        cursor.execute("SELECT COUNT(*) FROM czesc")
        if cursor.fetchone()[0] == 0:
            czesci_startowe = [
                ('Dysk SSD NVMe 1TB', 320.00, 5),
                ('Pamięć RAM DDR4 16GB', 180.00, 3),
                ('Bateria do laptopa (uniwersalna)', 210.00, 0),
                ('Matryca IPS 15.6" FullHD', 450.00, 0),
                ('Pasta termoprzewodząca Thermal Grizzly', 45.00, 12),
                ('Układ zasilania USB-C', 95.00, 1)
            ]
            cursor.executemany("INSERT INTO czesc (nazwa, cena, dostepnosc) VALUES (?, ?, ?)", czesci_startowe)

        db.commit()


# --- WIDOKI CYKL 1 & AKTUALIZACJE CYKL 2 ---

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

        cursor.execute("INSERT INTO klient (imie, nazwisko, telefon, email) VALUES (?, ?, ?, ?)",
                       (imie, nazwisko, telefon, email))
        klient_id = cursor.lastrowid

        cursor.execute("INSERT INTO formularz_zgloszenia (opis_problemu, klient_id) VALUES (?, ?)",
                       (opis, klient_id))
        formularz_id = cursor.lastrowid

        cursor.execute("INSERT INTO urzadzenie (typ_sprzetu, model) VALUES (?, ?)",
                       (typ_sprzetu, model))
        urzadzenie_id = cursor.lastrowid

        numer_zlecenia = "IRIS-" + ''.join(random.choices(string.digits, k=4))

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
    """W04 (aktualizacja Cykl 2): Status Zlecenia, Anulowanie oraz Akceptacja/Odrzucenie Kosztorysu (F04, F06)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        SELECT z.*, u.typ_sprzetu, u.model, k.imie, k.email, f.opis_problemu
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        WHERE z.numer = ?
    """, (numer,))
    zlecenie = cursor.fetchone()

    if not zlecenie:
        return render_template('w01_index.html', error="Nie znaleziono zlecenia.")

    # Pobranie powiązanego kosztorysu i diagnozy (jeśli istnieją)
    cursor.execute("SELECT * FROM kosztorys WHERE zlecenie_id = ?", (zlecenie['id'],))
    kosztorys = cursor.fetchone()

    cursor.execute("""
        SELECT n.*, t.imie AS technik_imie, t.nazwisko AS technik_nazwisko
        FROM naprawa n
        LEFT JOIN technik t ON n.technik_id = t.id
        WHERE n.zlecenie_id = ?
    """, (zlecenie['id'],))
    naprawa = cursor.fetchone()

    error_msg = None
    success_msg = None

    if request.method == 'POST':
        akcja = request.form.get('akcja', 'anuluj')

        # F04: Anulowanie zlecenia przed dostarczeniem sprzętu
        if akcja == 'anuluj':
            if zlecenie['status'] == 'NEW':
                cursor.execute("UPDATE zlecenie SET status = 'CANCELLED' WHERE numer = ?", (numer,))
                cursor.execute("INSERT INTO anulowanie (powod, zlecenie_id) VALUES ('Anulowane przez klienta online', ?)", (zlecenie['id'],))
                db.commit()
                return redirect(url_for('w04_status', numer=numer))
            else:
                error_msg = "Nie można anulować zlecenia. Sprzęt został już dostarczony do serwisu."

        # F06: Decyzja klienta w sprawie kosztorysu (AKCEPTUJ / ODRZUC)
        elif akcja in ('akceptuj_kosztorys', 'odrzuc_kosztorys'):
            if not kosztorys:
                error_msg = "Brak kosztorysu przypisanego do tego zlecenia."
            elif zlecenie['status'] != 'IN_PROGRESS' or kosztorys['status_akceptacji'] != 'OCZEKUJE':
                error_msg = "Decyzja w sprawie kosztorysu została już podjęta lub status zlecenia nie pozwala na jej zmianę."
            else:
                if akcja == 'akceptuj_kosztorys':
                    cursor.execute("UPDATE kosztorys SET status_akceptacji = 'AKCEPTOWANY' WHERE id = ?", (kosztorys['id'],))
                    db.commit()
                    return redirect(url_for('w04_status', numer=numer))
                elif akcja == 'odrzuc_kosztorys':
                    cursor.execute("UPDATE kosztorys SET status_akceptacji = 'ODRZUCONY' WHERE id = ?", (kosztorys['id'],))
                    cursor.execute("UPDATE zlecenie SET status = 'COMPLETED' WHERE id = ?", (zlecenie['id'],))
                    db.commit()
                    return redirect(url_for('w04_status', numer=numer))

    return render_template(
        'w04_status.html',
        zlecenie=zlecenie,
        kosztorys=kosztorys,
        naprawa=naprawa,
        error=error_msg,
        message=success_msg
    )


@app.route('/panel-technika', methods=['GET', 'POST'])
def w05_tech():
    """W05: Panel Technika – Przyjęcie Sprzętu oraz nawigacja do W06 i W07"""
    db = get_db()
    cursor = db.cursor()

    message = None
    if request.method == 'POST':
        akcja = request.form.get('akcja', 'przyjmij')
        numer = request.form.get('numer', '').strip()
        cursor.execute("SELECT * FROM zlecenie WHERE numer = ?", (numer,))
        zlecenie = cursor.fetchone()

        if not zlecenie:
            message = "Nie znaleziono zlecenia o takim numerze."
        elif akcja == 'przyjmij':
            if zlecenie['status'] == 'NEW':
                cursor.execute("UPDATE zlecenie SET status = 'DELIVERED' WHERE numer = ?", (numer,))
                db.commit()
                message = f"Zlecenie {numer} zostało przyjęte (status zmieniony na DELIVERED)."
            else:
                message = f"Zlecenie ma już status: {zlecenie['status']} (nie można zmienić na DELIVERED)."
        elif akcja == 'zakoncz':
            # Zakończenie fizycznej naprawy po akceptacji kosztorysu
            cursor.execute("SELECT * FROM kosztorys WHERE zlecenie_id = ?", (zlecenie['id'],))
            kosztorys = cursor.fetchone()
            if zlecenie['status'] == 'IN_PROGRESS' and kosztorys and kosztorys['status_akceptacji'] == 'AKCEPTOWANY':
                cursor.execute("UPDATE zlecenie SET status = 'COMPLETED' WHERE id = ?", (zlecenie['id'],))
                db.commit()
                message = f"Naprawa zlecenia {numer} została ukończona (status zmieniony na COMPLETED)."
            else:
                message = f"Nie można zakończyć zlecenia {numer}. Wymagany status IN_PROGRESS oraz zaakceptowany kosztorys."

    cursor.execute("""
        SELECT z.id, z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwisko AS nazwisko,
               ko.kwota AS kosztorys_kwota, ko.status_akceptacji AS kosztorys_status
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        LEFT JOIN kosztorys ko ON z.id = ko.zlecenie_id
        ORDER BY z.id DESC
    """)
    zlecenia = cursor.fetchall()

    return render_template('w05_tech.html', zlecenia=zlecenia, message=message)


# --- NOWE WIDOKI CYKL 2 (W06 i W07) ---

@app.route('/panel-technika/diagnoza/<numer>', methods=['GET', 'POST'])
def w06_diagnoza(numer):
    """W06: Panel Technika – Diagnoza i Kosztorys (F05)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        SELECT z.*, u.typ_sprzetu, u.model, k.imie, k.nazwisko, f.opis_problemu
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        WHERE z.numer = ?
    """, (numer,))
    zlecenie = cursor.fetchone()

    if not zlecenie:
        return redirect(url_for('w05_tech'))

    cursor.execute("SELECT * FROM technik")
    technicy = cursor.fetchall()

    cursor.execute("SELECT * FROM kosztorys WHERE zlecenie_id = ?", (zlecenie['id'],))
    kosztorys = cursor.fetchone()

    cursor.execute("""
        SELECT n.*, t.imie AS technik_imie, t.nazwisko AS technik_nazwisko
        FROM naprawa n
        LEFT JOIN technik t ON n.technik_id = t.id
        WHERE n.zlecenie_id = ?
    """, (zlecenie['id'],))
    naprawa = cursor.fetchone()

    error = None
    message = None

    if request.method == 'POST':
        opis = request.form.get('opis', '').strip()
        czas_naprawy = request.form.get('czas_naprawy', '').strip()
        kwota_raw = request.form.get('kwota', '').strip().replace(',', '.')
        technik_id = request.form.get('technik_id')

        # Warunek poprawności F05: zlecenie musi być w stanie DELIVERED
        if zlecenie['status'] != 'DELIVERED':
            error = f"Nie można utworzyć kosztorysu dla zlecenia o statusie {zlecenie['status']}. Wymagany status: DELIVERED."
        elif not opis or not czas_naprawy or not kwota_raw or not technik_id:
            error = "Wszystkie pola diagnozy i kosztorysu są wymagane."
        else:
            try:
                kwota = float(kwota_raw)
                czas_int = int(czas_naprawy)
                if kwota <= 0:
                    error = "Kwota kosztorysu musi być większa od 0."
                elif czas_int <= 0:
                    error = "Szacowany czas naprawy musi być większy od 0."
                else:
                    # Zapis rekordu NAPRAWA (B09)
                    cursor.execute("""
                        INSERT INTO naprawa (opis, czas_naprawy, zlecenie_id, technik_id)
                        VALUES (?, ?, ?, ?)
                    """, (opis, czas_int, zlecenie['id'], technik_id))

                    # Zapis rekordu KOSZTORYS (B08) ze stanem OCZEKUJE
                    cursor.execute("""
                        INSERT INTO kosztorys (kwota, status_akceptacji, zlecenie_id)
                        VALUES (?, 'OCZEKUJE', ?)
                    """, (round(kwota, 2), zlecenie['id']))

                    # Zmiana statusu zlecenia na IN_PROGRESS
                    cursor.execute("UPDATE zlecenie SET status = 'IN_PROGRESS' WHERE id = ?", (zlecenie['id'],))
                    db.commit()

                    return redirect(url_for('w06_diagnoza', numer=numer))
            except ValueError:
                error = "Wprowadź poprawne wartości liczbowe dla kwoty oraz czasu naprawy."

    return render_template(
        'w06_diagnoza.html',
        zlecenie=zlecenie,
        technicy=technicy,
        kosztorys=kosztorys,
        naprawa=naprawa,
        error=error,
        message=message
    )


@app.route('/panel-technika/czesci/<numer>', methods=['GET', 'POST'])
def w07_czesci(numer):
    """W07: Panel Technika – Przypisanie i Zamówienie Części (F07)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        SELECT z.*, u.typ_sprzetu, u.model, k.imie, k.nazwisko
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        WHERE z.numer = ?
    """, (numer,))
    zlecenie = cursor.fetchone()

    if not zlecenie:
        return redirect(url_for('w05_tech'))

    cursor.execute("SELECT * FROM kosztorys WHERE zlecenie_id = ?", (zlecenie['id'],))
    kosztorys = cursor.fetchone()

    error = None
    message = None

    if request.method == 'POST':
        akcja = request.form.get('akcja', 'przypisz')

        # Warunek poprawności F07: kosztorys musi być zaakceptowany (AKCEPTOWANY)
        if not kosztorys or kosztorys['status_akceptacji'] != 'AKCEPTOWANY':
            error = "Nie można przypisać ani zamówić części – kosztorys nie został jeszcze zaakceptowany przez klienta."
        elif zlecenie['status'] in ('CANCELLED', 'COMPLETED'):
            error = f"Nie można modyfikować części dla zlecenia o statusie {zlecenie['status']}."
        else:
            if akcja == 'przypisz':
                czesc_id = request.form.get('czesc_id')
                ilosc_raw = request.form.get('ilosc', '1')
                symuluj_blad_api = request.form.get('symuluj_blad_api') == '1'

                try:
                    ilosc = int(ilosc_raw)
                    if ilosc <= 0:
                        raise ValueError
                except ValueError:
                    error = "Ilość części musi być dodatnią liczbą całkowitą."

                if not error:
                    cursor.execute("SELECT * FROM czesc WHERE id = ?", (czesc_id,))
                    czesc = cursor.fetchone()
                    if not czesc:
                        error = "Wybrana część nie istnieje w katalogu."
                    else:
                        # Scenariusz A: Część dostępna na magazynie w wystarczającej ilości -> REZERWACJA
                        if czesc['dostepnosc'] >= ilosc:
                            nowa_dostepnosc = czesc['dostepnosc'] - ilosc
                            cursor.execute("UPDATE czesc SET dostepnosc = ? WHERE id = ?", (nowa_dostepnosc, czesc['id']))
                            cursor.execute("""
                                INSERT INTO zlecenie_czesc (zlecenie_id, czesc_id, ilosc, status_zamowienia)
                                VALUES (?, ?, ?, 'REZERWACJA')
                            """, (zlecenie['id'], czesc['id'], ilosc))
                            db.commit()
                            message = f"Zarezerwowano z magazynu: {czesc['nazwa']} ({ilosc} szt.)."

                        # Scenariusz B: Brak wystarczającej ilości na stanie -> Automatyczne zamówienie przez API hurtowni
                        else:
                            brakujaca_ilosc = ilosc - czesc['dostepnosc']
                            # Wyzerowanie ewentualnej resztki magazynowej na poczet zlecenia
                            if czesc['dostepnosc'] > 0:
                                cursor.execute("UPDATE czesc SET dostepnosc = 0 WHERE id = ?", (czesc['id'],))

                            # Status zlecenia przechodzi w WAITING_FOR_PARTS
                            cursor.execute("UPDATE zlecenie SET status = 'WAITING_FOR_PARTS' WHERE id = ?", (zlecenie['id'],))

                            ok, api_msg = WarehouseApiClient.send_order(
                                zlecenie_numer=zlecenie['numer'],
                                czesc_id=czesc['id'],
                                czesc_nazwa=czesc['nazwa'],
                                ilosc=brakujaca_ilosc,
                                simulate_error=symuluj_blad_api
                            )

                            if ok:
                                cursor.execute("""
                                    INSERT INTO zlecenie_czesc (zlecenie_id, czesc_id, ilosc, status_zamowienia)
                                    VALUES (?, ?, ?, 'ZAMOWIONE_HURTOWNIA')
                                """, (zlecenie['id'], czesc['id'], ilosc))
                                db.commit()
                                message = f"Brak części na magazynie. Status zlecenia: WAITING_FOR_PARTS. {api_msg}"
                            else:
                                # Sytuacja błędna F07: zapisanie stanu oczekiwania na ponownienie transmisji
                                cursor.execute("""
                                    INSERT INTO zlecenie_czesc (zlecenie_id, czesc_id, ilosc, status_zamowienia)
                                    VALUES (?, ?, ?, 'OCZEKUJE_PONOWIENIA_API')
                                """, (zlecenie['id'], czesc['id'], ilosc))
                                db.commit()
                                error = f"{api_msg} Zapisano stan oczekiwania na ponownienie transmisji."

            # Ponowienie nieudanej transmisji do API hurtowni
            elif akcja == 'ponow_api':
                zc_id = request.form.get('zc_id')
                cursor.execute("""
                    SELECT zc.*, c.nazwa
                    FROM zlecenie_czesc zc
                    JOIN czesc c ON zc.czesc_id = c.id
                    WHERE zc.id = ? AND zc.zlecenie_id = ?
                """, (zc_id, zlecenie['id']))
                zc = cursor.fetchone()
                if zc and zc['status_zamowienia'] == 'OCZEKUJE_PONOWIENIA_API':
                    ok, api_msg = WarehouseApiClient.send_order(
                        zlecenie_numer=zlecenie['numer'],
                        czesc_id=zc['czesc_id'],
                        czesc_nazwa=zc['nazwa'],
                        ilosc=zc['ilosc'],
                        simulate_error=False
                    )
                    if ok:
                        cursor.execute("UPDATE zlecenie_czesc SET status_zamowienia = 'ZAMOWIONE_HURTOWNIA' WHERE id = ?", (zc_id,))
                        db.commit()
                        message = f"Ponowna transmisja udana! {api_msg}"

            # Oznaczenie dostawy części z hurtowni (Scenariusz 7: powrót zlecenia do IN_PROGRESS)
            elif akcja == 'dostarczono_czesc':
                zc_id = request.form.get('zc_id')
                cursor.execute("UPDATE zlecenie_czesc SET status_zamowienia = 'DOSTARCZONE' WHERE id = ? AND zlecenie_id = ?", (zc_id, zlecenie['id']))
                # Sprawdzenie czy wszystkie części dla zlecenia są już gotowe (brak zamówień w toku)
                cursor.execute("""
                    SELECT COUNT(*) FROM zlecenie_czesc
                    WHERE zlecenie_id = ? AND status_zamowienia IN ('ZAMOWIONE_HURTOWNIA', 'OCZEKUJE_PONOWIENIA_API')
                """, (zlecenie['id'],))
                oczekujace = cursor.fetchone()[0]
                if oczekujace == 0 and zlecenie['status'] == 'WAITING_FOR_PARTS':
                    cursor.execute("UPDATE zlecenie SET status = 'IN_PROGRESS' WHERE id = ?", (zlecenie['id'],))
                    message = "Część dostarczona z hurtowni. Wszystkie części skompletowane – status zlecenia wrócił na IN_PROGRESS."
                else:
                    message = "Potwierdzono dostawę pozycji z hurtowni (DOSTARCZONE)."
                db.commit()

    # Odświeżenie danych do widoku
    cursor.execute("SELECT * FROM zlecenie WHERE id = ?", (zlecenie['id'],))
    zlecenie_aktualne = cursor.fetchone()

    cursor.execute("SELECT * FROM czesc ORDER BY nazwa ASC")
    czesci_magazyn = cursor.fetchall()

    cursor.execute("""
        SELECT zc.id, zc.ilosc, zc.status_zamowienia, c.nazwa, c.cena
        FROM zlecenie_czesc zc
        JOIN czesc c ON zc.czesc_id = c.id
        WHERE zc.zlecenie_id = ?
        ORDER BY zc.id DESC
    """, (zlecenie['id'],))
    przypisane_czesci = cursor.fetchall()

    return render_template(
        'w07_czesci.html',
        zlecenie=zlecenie_aktualne,
        urzadzenie=f"{zlecenie['typ_sprzetu']} - {zlecenie['model']}",
        klient=f"{zlecenie['imie']} {zlecenie['nazwisko'] or ''}".strip(),
        kosztorys=kosztorys,
        czesci_magazyn=czesci_magazyn,
        przypisane_czesci=przypisane_czesci,
        error=error,
        message=message
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

```

---

### 2. Zaktualizowany szablon `templates/w04_status.html` (W04 – Akceptacja Kosztorysu)

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Status Zlecenia i Kosztorys - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 650px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .box { border: 1px solid #ccc; padding: 15px; margin: 15px 0; background: #fafafa; border-radius: 5px; }
        .estimate-box { border: 2px solid #007bff; padding: 15px; margin: 15px 0; background: #f0f7ff; border-radius: 5px; }
        .error { color: #721c24; background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        button { border: none; padding: 10px 15px; cursor: pointer; font-weight: bold; border-radius: 4px; }
        button.cancel { background: #dc3545; color: white; width: 100%; }
        button.accept { background: #28a745; color: white; width: 48%; }
        button.reject { background: #dc3545; color: white; width: 48%; float: right; }
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <h2>Wynik Wyszukiwania Statusu</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}

    <div class="box">
        <p><strong>Zlecenie NR:</strong> {{ zlecenie.numer }}</p>
        <p><strong>Urządzenie:</strong> {{ zlecenie.typ_sprzetu }} - {{ zlecenie.model }}</p>
        <p><strong>Zgłoszony problem:</strong> {{ zlecenie.opis_problemu }}</p>
        <p><strong>Klient:</strong> {{ zlecenie.imie }} ({{ zlecenie.email }})</p>
        <p><strong>Aktualny Status:</strong> <span style="color: #007bff; font-weight: bold;">{{ zlecenie.status }}</span></p>
    </div>

    <!-- Sekcja Diagnozy i Kosztorysu (Cykl 2 - F06) -->
    {% if kosztorys %}
    <div class="estimate-box">
        <h3>Wynik Diagnozy i Kosztorys Naprawy</h3>
        {% if naprawa %}
            <p><strong>Diagnoza technika ({{ naprawa.technik_imie }} {{ naprawa.technik_nazwisko }}):</strong><br>{{ naprawa.opis }}</p>
            <p><strong>Szacowany czas realizacji:</strong> {{ naprawa.czas_naprawy }} godz.</p>
        {% endif %}
        <p style="font-size: 1.2em;"><strong>Kwota kosztorysu:</strong> {{ "%.2f"|format(kosztorys.kwota) }} PLN</p>
        <p><strong>Status wyceny:</strong>
            {% if kosztorys.status_akceptacji == 'OCZEKUJE' %}
                <span class="badge" style="background: #ffc107; color: #000;">OCZEKUJE NA DECYZJĘ KLIENTA</span>
            {% elif kosztorys.status_akceptacji == 'AKCEPTOWANY' %}
                <span class="badge" style="background: #28a745; color: #fff;">AKCEPTOWANY</span>
            {% elif kosztorys.status_akceptacji == 'ODRZUCONY' %}
                <span class="badge" style="background: #dc3545; color: #fff;">ODRZUCONY</span>
            {% endif %}
        </p>

        {% if zlecenie.status == 'IN_PROGRESS' and kosztorys.status_akceptacji == 'OCZEKUJE' %}
            <hr>
            <p>Prosimy o decyzję w sprawie realizacji naprawy zgodnie z powyższą wyceną:</p>
            <form method="POST" onsubmit="return confirm('Czy na pewno chcesz zatwierdzić tę decyzję? Po jej podjęciu nie będzie można jej zmienić.');">
                <button type="submit" name="akcja" value="akceptuj_kosztorys" class="accept">Akceptuj kosztorys</button>
                <button type="submit" name="akcja" value="odrzuc_kosztorys" class="reject">Odrzuć kosztorys</button>
                <div style="clear: both;"></div>
            </form>
        {% elif kosztorys.status_akceptacji == 'AKCEPTOWANY' %}
            <p style="color: #155724;"><em>Kosztorys został zaakceptowany. Serwis realizuje naprawę.</em></p>
        {% elif kosztorys.status_akceptacji == 'ODRZUCONY' %}
            <p style="color: #721c24;"><em>Kosztorys został odrzucony. Naprawa została zaniechana, sprzęt jest gotowy do odbioru.</em></p>
        {% endif %}
    </div>
    {% endif %}

    <!-- Anulowanie przed dostarczeniem sprzętu (Cykl 1 - F04) -->
    {% if zlecenie.status == 'NEW' %}
        <form method="POST">
            <input type="hidden" name="akcja" value="anuluj">
            <button type="submit" class="cancel">Anuluj Zamówienie</button>
        </form>
    {% elif zlecenie.status == 'DELIVERED' %}
        <p style="color: gray;"><em>Sprzęt został dostarczony do serwisu i oczekuje na diagnozę technika.</em></p>
    {% elif zlecenie.status == 'WAITING_FOR_PARTS' %}
        <p style="color: #856404;"><em>Oczekiwanie na dostawę brakujących części z hurtowni.</em></p>
    {% elif zlecenie.status == 'COMPLETED' %}
        <p style="color: #155724;"><strong>Zlecenie zakończone. Sprzęt gotowy do odbioru w serwisie.</strong></p>
    {% elif zlecenie.status == 'CANCELLED' %}
        <p style="color: red;"><em>To zlecenie zostało anulowane.</em></p>
    {% endif %}

    <br>
    <a href="{{ url_for('w01_index') }}">Powrót do strony głównej</a>
</div>
</body>
</html>

```

---

### 3. Zaktualizowany szablon `templates/w05_tech.html` (W05 – Panel Technika z przejściami do W06 i W07)

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Panel Technika - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 1000px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }
        th { background: #333; color: white; }
        .msg { background: #e2f0d9; padding: 10px; margin-bottom: 15px; border: 1px solid #c8e1b9; }
        input, button { padding: 8px; margin: 5px 0; }
        button { background: #17a2b8; color: white; border: none; cursor: pointer; border-radius: 3px; }
        .btn-link { display: inline-block; padding: 5px 8px; text-decoration: none; color: white; border-radius: 3px; font-size: 12px; margin-right: 4px; }
        .btn-diag { background: #007bff; }
        .btn-parts { background: #6f42c1; }
        .btn-done { background: #28a745; padding: 5px 8px; font-size: 12px; margin: 0; }
    </style>
</head>
<body>
<div class="container">
    <h2>Panel Technika – Zarządzanie Zleceniami</h2>

    {% if message %}<div class="msg">{{ message }}</div>{% endif %}

    <form method="POST">
        <input type="hidden" name="akcja" value="przyjmij">
        <label>Podaj ID / Numer zlecenia od klienta (Przyjęcie sprzętu):</label><br>
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
            <th>Status Zlecenia</th>
            <th>Kosztorys</th>
            <th>Akcje Technika (Cykl 2)</th>
        </tr>
        {% for z in zlecenia %}
        <tr>
            <td><strong>{{ z.numer }}</strong></td>
            <td>{{ z.imie }} {{ z.nazwisko or '' }}</td>
            <td>{{ z.typ_sprzetu }} - {{ z.model }}</td>
            <td><strong>{{ z.status }}</strong></td>
            <td>
                {% if z.kosztorys_kwota %}
                    {{ "%.2f"|format(z.kosztorys_kwota) }} PLN ({{ z.kosztorys_status }})
                {% else %}
                    <span style="color: gray;">Brak</span>
                {% endif %}
            </td>
            <td>
                {% if z.status != 'NEW' and z.status != 'CANCELLED' %}
                    <a href="{{ url_for('w06_diagnoza', numer=z.numer) }}" class="btn-link btn-diag">Diagnoza / Kosztorys (W06)</a>
                    <a href="{{ url_for('w07_czesci', numer=z.numer) }}" class="btn-link btn-parts">Części (W07)</a>
                {% else %}
                    <span style="color: gray; font-size: 12px;">Oczekuje na dostarczenie / anulowane</span>
                {% endif %}

                {% if z.status == 'IN_PROGRESS' and z.kosztorys_status == 'AKCEPTOWANY' %}
                    <form method="POST" style="display: inline;">
                        <input type="hidden" name="akcja" value="zakoncz">
                        <input type="hidden" name="numer" value="{{ z.numer }}">
                        <button type="submit" class="btn-done">Zakończ naprawę</button>
                    </form>
                {% endif %}
            </td>
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

### 4. Nowy szablon `templates/w06_diagnoza.html` (W06 – Diagnoza i Kosztorys)

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Diagnoza i Kosztorys (W06) - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 700px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .box { border: 1px solid #ddd; padding: 15px; background: #fafafa; margin-bottom: 20px; border-radius: 5px; }
        .error { color: #721c24; background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .msg { background: #e2f0d9; padding: 10px; margin-bottom: 15px; border: 1px solid #c8e1b9; }
        input, select, textarea, button { padding: 8px; margin: 5px 0 15px 0; width: 100%; box-sizing: border-box; }
        button { background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
<div class="container">
    <h2>Panel Technika – Diagnoza i Kosztorys (W06)</h2>

    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    {% if message %}<div class="msg">{{ message }}</div>{% endif %}

    <div class="box">
        <p><strong>Zlecenie:</strong> {{ zlecenie.numer }} | <strong>Status:</strong> {{ zlecenie.status }}</p>
        <p><strong>Urządzenie:</strong> {{ zlecenie.typ_sprzetu }} - {{ zlecenie.model }}</p>
        <p><strong>Klient:</strong> {{ zlecenie.imie }} {{ zlecenie.nazwisko or '' }}</p>
        <p><strong>Opis usterki od klienta:</strong> {{ zlecenie.opis_problemu }}</p>
    </div>

    {% if kosztorys %}
        <div class="box" style="border-color: #28a745; background: #f3fbf5;">
            <h3>Zapisana Diagnoza i Kosztorys</h3>
            {% if naprawa %}
                <p><strong>Technik prowadzący:</strong> {{ naprawa.technik_imie }} {{ naprawa.technik_nazwisko }}</p>
                <p><strong>Opis diagnozy:</strong> {{ naprawa.opis }}</p>
                <p><strong>Szacowany czas naprawy:</strong> {{ naprawa.czas_naprawy }} godz.</p>
            {% endif %}
            <p><strong>Kwota kosztorysu:</strong> {{ "%.2f"|format(kosztorys.kwota) }} PLN</p>
            <p><strong>Status akceptacji przez klienta:</strong> <strong>{{ kosztorys.status_akceptacji }}</strong></p>
        </div>
        <a href="{{ url_for('w07_czesci', numer=zlecenie.numer) }}"><button style="background: #6f42c1;">Przejdź do przypisania części (W07)</button></a>
    {% elif zlecenie.status == 'DELIVERED' %}
        <form method="POST">
            <label>Technik wykonujący diagnozę:</label>
            <select name="technik_id" required>
                {% for t in technicy %}
                    <option value="{{ t.id }}">{{ t.imie }} {{ t.nazwisko }}</option>
                {% endfor %}
            </select>

            <label>Opis diagnozy technicznej:</label>
            <textarea name="opis" rows="4" placeholder="Wpisz wynik diagnozy oraz zakres prac naprawczych..." required></textarea>

            <label>Szacowany czas naprawy (w godzinach):</label>
            <input type="number" name="czas_naprawy" min="1" value="2" required>

            <label>Kwota kosztorysu (PLN):</label>
            <input type="number" name="kwota" step="0.01" min="0.01" placeholder="np. 250.00" required>

            <button type="submit">Zapisz diagnozę i udostępnij kosztorys klientowi</button>
        </form>
    {% else %}
        <p style="color: #721c24;">Nie można utworzyć kosztorysu dla zlecenia w stanie <strong>{{ zlecenie.status }}</strong>.</p>
    {% endif %}

    <br>
    <a href="{{ url_for('w05_tech') }}">Powrót do Panelu Technika (W05)</a>
</div>
</body>
</html>

```

---

### 5. Nowy szablon `templates/w07_czesci.html` (W07 – Przypisanie i Zamówienie Części)

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Części i Zamówienia (W07) - Iris Solutions</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; max-width: 850px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .box { border: 1px solid #ddd; padding: 15px; background: #fafafa; margin-bottom: 20px; border-radius: 5px; }
        .error { color: #721c24; background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .msg { background: #e2f0d9; padding: 10px; margin-bottom: 15px; border: 1px solid #c8e1b9; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #333; color: white; }
        input[type="number"], select { padding: 8px; margin: 5px 0 12px 0; width: 100%; box-sizing: border-box; }
        button { padding: 8px 12px; background: #6f42c1; color: white; border: none; cursor: pointer; border-radius: 4px; font-weight: bold; }
        .btn-small { padding: 5px 8px; font-size: 12px; }
        .btn-warn { background: #e0a800; color: #000; }
        .btn-ok { background: #28a745; }
    </style>
</head>
<body>
<div class="container">
    <h2>Panel Technika – Przypisanie i Zamówienie Części (W07)</h2>

    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    {% if message %}<div class="msg">{{ message }}</div>{% endif %}

    <div class="box">
        <p><strong>Zlecenie:</strong> {{ zlecenie.numer }} | <strong>Aktualny status:</strong> <span style="color: #007bff; font-weight: bold;">{{ zlecenie.status }}</span></p>
        <p><strong>Urządzenie:</strong> {{ urzadzenie }} | <strong>Klient:</strong> {{ klient }}</p>
        <p><strong>Status kosztorysu:</strong>
            {% if kosztorys %}
                <strong>{{ kosztorys.status_akceptacji }}</strong> ({{ "%.2f"|format(kosztorys.kwota) }} PLN)
            {% else %}
                <span style="color: red;">Brak kosztorysu</span>
            {% endif %}
        </p>
    </div>

    {% if kosztorys and kosztorys.status_akceptacji == 'AKCEPTOWANY' and zlecenie.status not in ('COMPLETED', 'CANCELLED') %}
        <h3>Dodaj część do naprawy</h3>
        <form method="POST">
            <input type="hidden" name="akcja" value="przypisz">

            <label>Wybierz część z katalogu magazynowego:</label>
            <select name="czesc_id" required>
                {% for c in czesci_magazyn %}
                    <option value="{{ c.id }}">
                        {{ c.nazwa }} — {{ "%.2f"|format(c.cena) }} PLN (Stan magazynowy: {{ c.dostepnosc }} szt.)
                    </option>
                {% endfor %}
            </select>

            <label>Ilość (szt.):</label>
            <input type="number" name="ilosc" min="1" value="1" required>

            <label style="display: block; margin-bottom: 15px; font-size: 13px; color: #555;">
                <input type="checkbox" name="symuluj_blad_api" value="1">
                Symuluj błąd komunikacji z zewnętrznym API hurtowni (test ścieżki błędnej F07)
            </label>

            <button type="submit">Przypisz część (lub zamów automatycznie z hurtowni)</button>
        </form>
    {% else %}
        <p style="color: #856404; background: #fff3cd; padding: 10px; border-radius: 4px;">
            Przypisywanie i zamawianie części jest możliwe wyłącznie po zaakceptowaniu kosztorysu przez klienta (status: <strong>AKCEPTOWANY</strong>) i przed zakończeniem zlecenia.
        </p>
    {% endif %}

    <hr>

    <h3>Części przypisane do zlecenia {{ zlecenie.numer }}:</h3>
    {% if przypisane_czesci %}
    <table>
        <tr>
            <th>Nazwa części</th>
            <th>Ilość</th>
            <th>Cena jedn.</th>
            <th>Status zamówienia</th>
            <th>Akcje</th>
        </tr>
        {% for pc in przypisane_czesci %}
        <tr>
            <td>{{ pc.nazwa }}</td>
            <td>{{ pc.ilosc }} szt.</td>
            <td>{{ "%.2f"|format(pc.cena) }} PLN</td>
            <td><strong>{{ pc.status_zamowienia }}</strong></td>
            <td>
                {% if pc.status_zamowienia == 'OCZEKUJE_PONOWIENIA_API' %}
                    <form method="POST" style="display: inline;">
                        <input type="hidden" name="akcja" value="ponow_api">
                        <input type="hidden" name="zc_id" value="{{ pc.id }}">
                        <button type="submit" class="btn-small btn-warn">Ponów wysyłkę do API</button>
                    </form>
                {% elif pc.status_zamowienia == 'ZAMOWIONE_HURTOWNIA' %}
                    <form method="POST" style="display: inline;">
                        <input type="hidden" name="akcja" value="dostarczono_czesc">
                        <input type="hidden" name="zc_id" value="{{ pc.id }}">
                        <button type="submit" class="btn-small btn-ok">Potwierdź dostawę z hurtowni</button>
                    </form>
                {% else %}
                    <span style="color: green;">Gotowe</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
        <p style="color: gray;">Brak przypisanych części do tego zlecenia.</p>
    {% endif %}

    <a href="{{ url_for('w05_tech') }}">Powrót do Panelu Technika (W05)</a>
</div>
</body>
</html>

```