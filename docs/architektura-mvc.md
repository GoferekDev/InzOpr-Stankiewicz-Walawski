# Architektura MVC – Iris Solutions (MVP 1.0)

## 1. Cel i stos technologiczny
* **Cel systemu:** Internetowa aplikacja do obsługi zleceń serwisowych dla małych przedsiębiorstw usługowych (zgłaszanie usterek, sprawdzanie statusu, anulowanie zlecenia przez klienta oraz przyjmowanie sprzętu przez technika).
* **Technologie:** Python 3, Flask, SQLite (`sqlite3`).

## 2. Mapa plików i podział odpowiedzialności (MVC)

| Warstwa | Plik / Katalog | Odpowiedzialność |
| :--- | :--- | :--- |
| **Punkt wejścia** | `iris-system/app.py` | Tworzenie instancji aplikacji Flask, inicjalizacja bazy danych, rejestracja Blueprintu kontrolera oraz zamykanie połączenia po żądaniu. |
| **Model (M)** | `iris-system/db.py` | Zarządzanie połączeniem SQLite (`get_db`, `close_connection`), wymuszenie `PRAGMA foreign_keys = ON`, tworzenie schematu tabel oraz inicjalizacja danych słownikowych (`kategoria_uslugi`). |
| **Model (M)** | `iris-system/models/zlecenie.py` | Logika biznesowa, walidacja danych wejściowych, generowanie unikalnego numeru `IRIS-XXXX`, zapytania parametryzowane SQL oraz kontrola przejść statusów (`NEW` -> `CANCELLED` / `DELIVERED`). |
| **Kontroler (C)** | `iris-system/controllers/zlecenia.py` | Obsługa żądań HTTP (`GET`/`POST`) dla tras `W01`–`W05`, pobieranie parametrów formularzy, wywoływanie funkcji modelu oraz wybór szablonu lub przekierowania. |
| **Widok (V)** | `iris-system/templates/w01_index.html` | Strona główna z wyszukiwarką statusu zlecenia oraz nawigacją do formularza zgłoszeniowego i panelu technika. |
| **Widok (V)** | `iris-system/templates/w02_form.html` | Formularz zgłoszenia usterki przez klienta wraz z wyświetlaniem komunikatów walidacji. |
| **Widok (V)** | `iris-system/templates/w03_success.html` | Ekran potwierdzenia utworzenia zgłoszenia z wygenerowanym numerem `IRIS-XXXX`. |
| **Widok (V)** | `iris-system/templates/w04_status.html` | Podgląd szczegółów i statusu zlecenia oraz przycisk anulowania (aktywny wyłącznie dla statusu `NEW`). |
| **Widok (V)** | `iris-system/templates/w05_tech.html` | Panel technika umożliwiający przyjęcie sprzętu (`DELIVERED`) oraz podgląd tabeli wszystkich zleceń. |

## 3. Funkcje MVP 1.0 i przepływ danych

1. **F01 – Zgłoszenie nowego zlecenia (`GET/POST /zgloszenie` -> `GET /sukces/<numer>`):**
   * Kontroler `w02_form()` przekazuje dane z formularza do `utworz_zlecenie(dane)` w modelu.
   * Model waliduje pola wymagane (`imie`, `email`, `typ_sprzetu`, `model`, `opis`), zapisuje rekordy w tabelach `klient`, `formularz_zgloszenia`, `urzadzenie` oraz `zlecenie` ze statusem `NEW`, a następnie zwraca unikalny numer `IRIS-XXXX`.
   * Kontroler przekierowuje użytkownika do `w03_success`.
2. **F02 – Sprawdzenie statusu zlecenia (`GET/POST /` -> `GET /status/<numer>`):**
   * Kontroler `w01_index()` przekazuje wpisany numer do `pobierz_zlecenie_po_numerze(numer)`.
   * W przypadku istnienia rekordu następuje przekierowanie do `w04_status()`, który pobiera pełne dane złączeniem `JOIN` (`pobierz_szczegoly_zlecenia(numer)`) i renderuje `w04_status.html`.
3. **F03 – Anulowanie zlecenia przez klienta (`POST /status/<numer>`):**
   * Kontroler `w04_status()` wywołuje `anuluj_zlecenie(numer)`.
   * Model weryfikuje, czy aktualny status to `NEW` – jeśli tak, zmienia go na `CANCELLED` i zapisuje wpis w tabeli `anulowanie`; w przeciwnym razie zwraca komunikat błędu.
4. **F04 – Przyjęcie sprzętu przez technika (`GET/POST /panel-technika`):**
   * Kontroler `w05_tech()` dla żądania `POST` wywołuje `przyjmij_sprzet(numer)` (zmiana `NEW` -> `DELIVERED`), a następnie pobiera listę zleceń przez `pobierz_wszystkie_zlecenia()` i przekazuje ją do `w05_tech.html`.

## 4. Schemat bazy danych SQLite (`app.db`)
* `klient(id, imie, nazwisko, telefon, email)`
* `formularz_zgloszenia(id, opis_problemu, data_zgloszenia, klient_id)`
* `urzadzenie(id, typ_sprzetu, model)`
* `kategoria_uslugi(id, nazwa)`
* `zlecenie(id, numer, data_utworzenia, status, formularz_id, urzadzenie_id, kategoria_id)`
* `anulowanie(id, powod, zlecenie_id)`
