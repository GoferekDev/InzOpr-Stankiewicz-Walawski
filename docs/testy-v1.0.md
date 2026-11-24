# Raport testów odbiorczych – Iris Solutions v1.0.0

## Środowisko testowe
- **System operacyjny:** Windows
- **Środowisko:** Python 3.x, Flask, SQLite (`iris-system/app.db`)
- **Polecenie uruchomienia (z katalogu `iris-system`):**
* Windows: `.\.venv\Scripts\python.exe app.py`
* Linux/macOS: `.venv/bin/python app.py`

> **Uwaga metodologiczna:** Poniższa tabela zawiera przygotowane scenariusze testowe (przypadek poprawny, błędny oraz trwałość po restarcie) wraz z aktualnym statusem do uzupełnienia po uruchomieniu lokalnym na stanowiskach członków zespołu.

## Tabela wyników testów (F01–F04 + trwałość danych)

| ID | Funkcja MVP | Scenariusz i dane wejściowe | Oczekiwany wynik | Rzeczywisty wynik | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | **F01** – Formularz zgłoszeniowy (`W02` -> `W03`) | **Przypadek poprawny:** Wejście na `/zgloszenie`, wpisanie: Imię `Jan`, Nazwisko `Kowalski`, Telefon `500600700`, E-mail `jan@example.com`, Typ `Laptop`, Model `Dell XPS 13`, Kategoria `Serwisowe`, Opis `Nie włącza się`. | Zapis rekordów w `klient`, `formularz_zgloszenia`, `urzadzenie` i `zlecenie` (`status = 'NEW'`), przekierowanie na `/sukces/IRIS-XXXX` i wyświetlenie numeru zlecenia. | Dane zostały zapisane we wszystkich wymaganych tabelach. Przekierowano na /sukces/IRIS-4683 i wyświetlono numer zlecenia. | `wykonany` |
| **T02** | **F01** – Formularz zgłoszeniowy (`W02`) | **Przypadek błędny:** Wysłanie żądania `POST` na `/zgloszenie` z pustym polem wymaganym (np. brak `opis` lub `email`). | Brak zapisu do bazy danych; wyświetlenie komunikatu błędu `Wypełnij wszystkie wymagane pola.` na `w02_form.html`. | Została wyświetlona prośba o wypełnienie brakującego pola. Do bazy danych nie zostało nic zapisane. | `wykonany` |
| **T03** | **F02** – Sprawdzenie statusu (`W01` -> `W04`) | **Przypadek poprawny:** Wpisanie na stronie głównej `/` wygenerowanego numeru `IRIS-XXXX` z testu T01 i kliknięcie `Sprawdź`. | Przekierowanie na `/status/IRIS-XXXX`, wyświetlenie danych urządzenia, klienta oraz statusu `NEW` i przycisku `Anuluj Zamówienie`. | Przekierowano na /status/IRIS-4683. Wyświetlono dane klienta. | `wykonany` |
| **T04** | **F02** – Sprawdzenie statusu (`W01`) | **Przypadek błędny:** Wpisanie nieistniejącego numeru `IRIS-0000` na stronie `/`. | Pozostanie na stronie głównej z komunikatem `Nieprawidłowy numer zlecenia`. | Pozostano na stronie głównej i wyświetlono komunikat. | `wykonany` |
| **T05** | **F03** – Anulowanie zlecenia (`W04`) | **Przypadek poprawny:** Na stronie `/status/IRIS-XXXX` dla zlecenia ze statusem `NEW` kliknięcie `Anuluj Zamówienie`. | Zmiana statusu zlecenia na `CANCELLED`, dodanie rekordu w tabeli `anulowanie`, ukrycie przycisku anulowania i wyświetlenie informacji `To zlecenie zostało anulowane.`. | Wyświetlono informację i ukryto przycisk. Dodano rekord w tabeli. Status zlecenia zmieniony na CANCELLED. | `wykonany` |
| **T06** | **F04** – Przyjęcie sprzętu (`W05`) | **Przypadek poprawny:** Utworzenie nowego zlecenia (`NEW`), przejście do `/panel-technika`, wpisanie numeru zlecenia i kliknięcie `Potwierdź przyjęcie sprzętu`. | Zmiana statusu na `DELIVERED`, komunikat `Zlecenie IRIS-XXXX zostało przyjęte (status zmieniony na DELIVERED).` oraz aktualizacja tabeli zleceń. | Stan w tabeli został zaktualizowany. Został wyświetlony komunikat. | `wykonany` |
| **T07** | **F04** – Przyjęcie sprzętu (`W05`) | **Przypadek błędny:** Wpisanie w panelu technika nieistniejącego numeru `IRIS-9999` lub zlecenia już anulowanego (`CANCELLED`). | Brak zmiany w bazie; wyświetlenie komunikatu `Nie znaleziono zlecenia o takim numerze.` lub `Zlecenie ma już status: CANCELLED.`. | Brak zmian w bazie danych. Wyświetlenie odpowiedniego komunikatu dla każdego przypadku. | `wykonany` |
| **T08** | **F03** – Blokada anulowania (`W04`) | **Przypadek błędny:** Wejście na `/status/IRIS-XXXX` dla zlecenia przyjętego przez technika (`DELIVERED`) i próba wysłania `POST` anulowania. | Brak zmiany statusu (`DELIVERED`), wyświetlenie komunikatu o braku możliwości anulowania online. | Wejście na stronę statusu urządzenia o stanie DELIVERED nie wyświetla przycisku anulowania. Próba manualnego wysłania POST nie wydaję się działać. | `wykonany` |
| **T09** | **Trwałość danych** | **Restart aplikacji:** Zatrzymanie serwera Flask (`Ctrl+C`), ponowne uruchomienie `app.py` oraz sprawdzenie listy w `/panel-technika` i statusu w `/status/IRIS-XXXX`. | Wszystkie utworzone wcześniej zlecenia oraz ich zaktualizowane statusy (`CANCELLED`, `DELIVERED`) są nadal widoczne w bazie `app.db`. | Dane są widoczne w bazie, nawet po restarcie. | `wykonany` |
