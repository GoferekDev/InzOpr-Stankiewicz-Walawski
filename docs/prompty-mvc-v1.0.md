# Dokumentacja promptów i iteracji – Iris Solutions (MVP 1.0)

## 1. Porównanie promptu ogólnego i doprecyzowanego

* **Prompt ogólny (nieprecyzyjny):**
  > „Zrób aplikację do obsługi zleceń w MVC z bazą SQLite i panelem technika.”
  * *Dlaczego był niewystarczający:* Nie określał istniejącego schematu bazy danych (`klient`, `formularz_zgloszenia`, `urzadzenie`, `zlecenie`, `anulowanie`), istniejących nazw widoków (`w01_index.html`–`w05_tech.html`), dozwolonych przejść statusów (`NEW` -> `CANCELLED` / `DELIVERED`) ani sposobu odbioru zmian

* **Prompt precyzyjny (zastosowany):**
  > „W projekcie Iris Solutions (`app.py`, `w01_index.html`–`w05_tech.html`, SQLite z tabelami `klient`, `formularz_zgloszenia`, `urzadzenie`, `kategoria_uslugi`, `zlecenie`, `anulowanie`) wydziel warstwę bazy do `db.py`, logikę i zapytania SQL do `models/zlecenie.py`, a obsługę tras do `controllers/zlecenia.py`. Zachowaj istniejące szablony oraz parametryzowane zapytania SQL. Zwróć drzewo katalogów, pełny kod zmienionych plików oraz kroki sprawdzenia przypadków poprawnych, błędnych i zapisu po restarcie.”

---

## 2. Uzupełnione szablony P1–P4

### P1 – Plan MVP i mapa MVC
* **Narzędzie / Data:** Gemini, 2026-11-24
* **Treść promptu:**
  > Pomóż nam zaplanować MVP 1.0 projektu Iris Solutions.
  > Cel użytkownika: umożliwienie klientowi zgłoszenia usterki, sprawdzenia statusu i anulowania zlecenia o statusie NEW, a technikowi przyjęcia sprzętu (zmiana statusu na DELIVERED) z trwałym zapisem w SQLite.
  > Stos: Python, Flask, SQLite.
  > Zakres: F01 formularz zgłoszeniowy (W02->W03), F02 sprawdzenie statusu (W01->W04), F03 anulowanie zlecenia (W04), F04 przyjęcie sprzętu w panelu technika (W05).
  > Widoki i dane: W01 strona główna i wyszukiwarka numeru, W02 formularz zgłoszenia, W03 potwierdzenie z numerem IRIS-XXXX, W04 status i anulowanie, W05 panel technika; tabele: klient, formularz_zgloszenia, urzadzenie, kategoria_uslugi, zlecenie, anulowanie.
  > Aktualny stan i pliki: cała logika SQL i tras znajduje się w app.py, a widoki w plikach w01_index.html..w05_tech.html; w app.py init_db() wywoływane jest tylko w `__main__`.
  > Przygotuj plan wykorzystania istniejącego kodu z podziałem na model, widok i prosty kontroler. Dla każdej funkcji wskaż pliki MVC oraz warunek poprawności. Wypisz braki i założenia. Zachowaj uzgodniony zakres MVP. Wynik: mapa plików i kolejność małych zmian. Na tym etapie przedstaw plan.
* **Rzeczywisty wynik:** Uzyskano podział plików na `db.py`, `models/zlecenie.py`, `controllers/zlecenia.py`, `app.py` oraz `templates/w01_index.html`–`w05_tech.html` wraz z mapą funkcji F01–F04 i warunkami walidacji.

---

### P2 – Szkielet MVC i pierwsza ścieżka
* **Narzędzie / Data:** Gemini, 2026-11-24
* **Treść promptu:**
  > Wykonaj pierwszy etap zaakceptowanego planu dla projektu Iris Solutions: wydziel warstwę bazy (db.py), model (models/zlecenie.py) oraz kontroler tras (controllers/zlecenia.py), podłączając je w app.py.
  > Technologie: Python, Flask, SQLite.
  > Aktualne pliki: app.py oraz szablony w01_index.html, w02_form.html, w03_success.html, w04_status.html, w05_tech.html.
  > Wyodrębnij model, widoki i kontroler. Dostosuj istniejące połączenia między plikami i zachowaj działające funkcje oraz dane. Kontroler ma odbierać żądanie, wywoływać model i wybierać widok lub przekierowanie. Przygotuj działające ścieżki W01..W05 oparte na funkcjach modelu. Zwróć drzewo katalogów, pełny kod zmienionych plików, zależności i polecenia uruchomienia dla Windows oraz Linux/macOS. Kryterium: aplikacja startuje i pokazuje dane z modelu.
* **Rzeczywisty wynik:** Wygenerowano strukturę katalogów `models/` i `controllers/`, oddzielono warstwę SQL od tras HTTP oraz zachowano zgodność z odwołaniami `url_for(...)` w istniejących szablonach.

---

### P3 – Pojedyncza funkcja MVP (F03 – Anulowanie zlecenia)
* **Narzędzie / Data:** Gemini, 2026-11-24
* **Treść promptu:**
  > W aktualnym kodzie (models/zlecenie.py, controllers/zlecenia.py, templates/w04_status.html) wykonaj wyłącznie F03 - anulowanie zlecenia przez klienta w widoku W04.
  > Użytkownik: klient sprawdzający status zlecenia.
  > Dane wejściowe: numer zlecenia w URL (/status/<numer>) oraz żądanie POST z formularza anulowania.
  > Reguły modelu: zlecenie musi istnieć; anulować można tylko zlecenie ze statusem 'NEW' (aktualizacja statusu na 'CANCELLED' oraz wstawienie rekordu do tabeli anulowanie z zapytaniem parametryzowanym); dla statusu innego niż 'NEW' brak zmiany i zwrócenie komunikatu błędu.
  > Kontroler ma wywołać funkcję modelu i przekazać wynik lub komunikat błędu do widoku w04_status.html.
  > Przykład poprawny: zlecenie o statusie 'NEW' + POST -> status 'CANCELLED', wpis w tabeli 'anulowanie', komunikat na W04.
  > Przykład błędny: zlecenie o statusie 'DELIVERED' lub 'CANCELLED' + POST -> status bez zmian, komunikat o braku możliwości anulowania.
  > Zapisuj dane w obecnej bazie; używaj zapytań parametryzowanych. Zachowaj wcześniejsze funkcje. Zwróć zmienione pliki i kroki sprawdzenia przypadku poprawnego, błędnego oraz zapisu po restarcie.
* **Rzeczywisty wynik:** W modelu `models/zlecenie.py` utworzono funkcję `anuluj_zlecenie(numer, powod)` wymuszającą warunek `status == 'NEW'` i zapisującą rekord w tabeli `anulowanie` w ramach jednej transakcji (`db.commit()`).

---

### P4 – Diagnoza i poprawka przed odbiorem
* **Narzędzie / Data:** Gemini, 2026-11-24
* **Treść promptu:**
  > Sprawdź zgłoszoną niezgodność z MVP 1.0: wywołanie init_db() w app.py jest umieszczone wyłącznie wewnątrz bloku `if __name__ == '__main__':`, a ścieżka `DATABASE = 'app.db'` jest względna względem bieżącego katalogu roboczego.
  > Aktualne pliki: app.py, db.py, models/zlecenie.py.
  > Sposób uruchomienia i wersje narzędzi: uruchomienie z katalogu projektu lub innego katalogu, Python 3.x + Flask + sqlite3.
  > Kroki odtworzenia: 1. Uruchom aplikację z innego katalogu roboczego lub zaimportuj app bez bloku `__main__` na nowej/pustej bazie. 2. Wejdź na /zgloszenie lub /panel-technika.
  > Oczekiwane działanie: schemat bazy i kategorie usług inicjalizują się poprawnie, a plik bazy znajduje się w przewidywalnym miejscu.
  > Faktyczny wynik i komunikat: w przypadku braku zainicjalizowanych tabel lub uruchomienia z innego katalogu aplikacja może zgłosić `sqlite3.OperationalError: no such table` lub utworzyć pustą bazę w innym folderze.
  > Ustal przyczynę i zaproponuj najmniejszą poprawkę zachowującą podział MVC. Zwróć zmienione pliki, krótkie wyjaśnienie i scenariusze ponownego sprawdzenia tej funkcji oraz wcześniejszych funkcji. Odróżnij testy wykonane od proponowanych; potwierdzaj uruchomienie tylko wtedy, gdy rzeczywiście je wykonano.
* **Rzeczywisty wynik i poprawka:**
  * *Poprawka w promptcie / kodzie:* Zdefiniowano bezwzględną ścieżkę pliku bazy danych względem położenia pliku `db.py` (`BASE_DIR = os.path.dirname(os.path.abspath(__file__))`, `DEFAULT_DB_PATH = os.path.join(BASE_DIR, "app.db")`), przeniesiono `init_db()` do funkcji fabrycznej `create_app()` w `app.py` oraz dodano pętlę gwarantującą unikalność losowanego numeru `IRIS-XXXX` w `models/zlecenie.py`.
