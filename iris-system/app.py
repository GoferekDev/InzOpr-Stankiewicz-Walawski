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