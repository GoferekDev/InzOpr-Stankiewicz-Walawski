import random
import string
from werkzeug.security import check_password_hash
from db import get_db


def weryfikuj_technika(login, haslo):
    login_clean = (login or "").strip()
    if not login_clean or not haslo:
        return False

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, login, password_hash FROM technik WHERE login = ?",
        (login_clean,),
    )
    technik = cursor.fetchone()
    if not technik:
        return False

    return check_password_hash(technik["password_hash"], haslo)


def _generuj_numer_zlecenia(cursor):
    while True:
        numer = "IRIS-" + "".join(random.choices(string.digits, k=4))
        cursor.execute("SELECT 1 FROM zlecenie WHERE numer = ?", (numer,))
        if cursor.fetchone() is None:
            return numer


def pobierz_zlecenie_po_numerze(numer):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM zlecenie WHERE numer = ?", (numer,))
    return cursor.fetchone()


def pobierz_szczegoly_zlecenia(numer):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT z.*, u.typ_sprzetu, u.model, k.imie, k.email, k.nazwisko, k.telefon
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
        WHERE z.numer = ?
    """, (numer,))
    return cursor.fetchone()


def utworz_zlecenie(dane):
    imie = (dane.get("imie") or "").strip()
    nazwisko = (dane.get("nazwisko") or "").strip()
    telefon = (dane.get("telefon") or "").strip()
    email = (dane.get("email") or "").strip()
    typ_sprzetu = (dane.get("typ_sprzetu") or "").strip()
    model = (dane.get("model") or "").strip()
    kategoria_id = dane.get("kategoria_id")
    opis = (dane.get("opis") or "").strip()

    if not all([imie, email, typ_sprzetu, model, opis]):
        return False, None, "Wypełnij wszystkie wymagane pola."

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO klient (imie, nazwisko, telefon, email) VALUES (?, ?, ?, ?)",
        (imie, nazwisko, telefon, email),
    )
    klient_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO formularz_zgloszenia (opis_problemu, klient_id) VALUES (?, ?)",
        (opis, klient_id),
    )
    formularz_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO urzadzenie (typ_sprzetu, model) VALUES (?, ?)",
        (typ_sprzetu, model),
    )
    urzadzenie_id = cursor.lastrowid

    numer_zlecenia = _generuj_numer_zlecenia(cursor)
    cursor.execute("""
        INSERT INTO zlecenie (numer, status, formularz_id, urzadzenie_id, kategoria_id)
        VALUES (?, 'NEW', ?, ?, ?)
    """, (numer_zlecenia, formularz_id, urzadzenie_id, kategoria_id))

    db.commit()
    return True, numer_zlecenia, None


def anuluj_zlecenie(numer, powod="Anulowane przez klienta online"):
    zlecenie = pobierz_zlecenie_po_numerze(numer)
    if not zlecenie:
        return False, "Nie znaleziono zlecenia."

    if zlecenie["status"] != "NEW":
        return False, "Nie można anulować zlecenia. Sprzęt został już dostarczony do serwisu."

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE zlecenie SET status = 'CANCELLED' WHERE numer = ?", (numer,))
    cursor.execute(
        "INSERT INTO anulowanie (powod, zlecenie_id) VALUES (?, ?)",
        (powod, zlecenie["id"]),
    )
    db.commit()
    return True, None


def przyjmij_sprzet(numer):
    zlecenie = pobierz_zlecenie_po_numerze(numer)
    if not zlecenie:
        return False, "Nie znaleziono zlecenia o takim numerze."

    if zlecenie["status"] != "NEW":
        return False, f"Zlecenie ma już status: {zlecenie['status']}."

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE zlecenie SET status = 'DELIVERED' WHERE numer = ?", (numer,))
    db.commit()
    return True, f"Zlecenie {numer} zostało przyjęte (status zmieniony na DELIVERED)."


def pobierz_wszystkie_zlecenia():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwisko AS nazwisko
        FROM zlecenie z
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
    """)
    return cursor.fetchall()
