# Roadmap Implementacyjny Projektu: Iris

- Wersja dokumentu: 1.0
- Autorzy: Mateusz Walawski, Wiktor Stankiewicz

## Cykl 1:

## **Cel i Granice Wersji v1 (MVP)**:

Umożliwienie klientom cyfrowego rejestrowania zgłoszeń serwisowych online oraz sprawdzania i anulowania zlecenia, a także dostarczenie technikowi serwisu panelu do wyszukiwania zleceń i zmiany ich statusu.

## **Opis efektu wersji v1 dla Użytkownika**:

Klient po wejściu na stronę internetową zakładu wypełnia formularz zgłoszeniowy usterki i otrzymuje unikalny numer zlecenia. Przy użyciu tego numeru klient może w każdej chwili sprawdzić status realizacji naprawy lub anulować zlecenie przed fizycznym dostarczeniem sprzętu. Technik w zakładzie po podaniu przez klienta identyfikatora zlecenia wyszukuje je w panelu i przyjmuje sprzęt, zmieniając jego status w bazie danych.

# Widoki (W)

- W01: Strona Główna z Weryfikacją Statusu
- W02: Formularz Zgłoszeniowy Online
- W03: Potwierdzenie Zgłoszenia
- W04: Status Zlecenia i Anulowanie
- W05: Panel Technika – Przyjęcie Sprzętu

# Baza Danych (B)

- B01: KLIENT: id (PK, int), imie (varchar), nazwisko (varchar), telefon (varchar), email (varchar).
- B02: FORMULARZ_ZGLOSZENIA: id (PK, int), opis_problemu (text), data_zgloszenia (datetime), klient_id (FK -> KLIENT.id).
- B03: URZADZENIE: id (PK, int), typ_sprzetu (varchar), model (varchar).
- B04: KATEGORIA_USLUGI: id (PK, int), nazwa (varchar).
- B05: ZLECENIE: id (PK, int), numer (varchar, UQ), data_utworzenia (datetime), status (varchar: NEW, DELIVERED, CANCELLED), formularz_id (FK -> FORMULARZ_ZGLOSZENIA.id), urzadzenie_id (FK -> URZADZENIE.id), kategoria_id (FK -> KATEGORIA_USLUGI.id).
- B06: ANULOWANIE: id (PK, int), powod (varchar), zlecenie_id (FK -> ZLECENIE.id, UQ).

# Funkcjonalność (F)

### F01: Wypełnienie formularza zgłoszeniowego usterki (Online)

- Aktor: Klient
- Powiązany widok: W02 -> W03
- Potrzebne dane: B01, B02, B03, B05
- Oczekiwane działanie: Klient wypełnia pola i wysyła formularz. System tworzy rekordy w bazy danych, nadaje status NEW i wyświetla unikalny numer zlecenia.
- Warunek poprawności: Poprawny format adresu e-mail, uzupełnione pola opisowe.
- Sytuacja błędna: Brak wymaganych pól -> komunikat błędu walidacji (W02).

### F02: Wyszukanie zlecenia po ID i zmiana statusu na DELIVERED

- Aktor: Technik
- Powiązany widok: W05
- Potrzebne dane: B05
- Oczekiwane działanie: Technik wpisuje podany przez klienta numer zlecenia, pobiera jego dane i zmienia status z NEW na DELIVERED
- Warunek poprawności: Zlecenie istnieje w bazie danych i znajduje się w stanie NEW.
- Sytuacja błędna: Zlecenie ma status CANCELLED lub nie istnieje -> komunikat "Nieprawidłowy numer zlecenia".

### F03: Sprawdzanie statusu zlecenia przez klienta online

- Aktor: Klient
- Powiązany Widok: W01->W04
- Potrzebne dane: ZLECENIE (numer, status), URZADZENIE (model).
- Oczekiwane działanie: Klient podaje numer zlecenia w W01. System wyszukuje rekord i wyświetla w W04 aktualny status.
- Warunek poprawności: Wyświetlenie właściwego statusu przypisanego do zlecenia.
- Sytuacja błędna: Błędny identyfikator -> przekierowanie do widoku W05 z informacją o błędzie.

### F04: Anulowanie zlecenia online przed dostarczeniem sprzętu (CANCELLED)

- Aktor: Klient
- Powiązany widok: W04
- Potrzebne dane: ZLECENIE (status), ANULOWANIE.
- Oczekiwane działanie: Klient klika przycisk anulowania w W04. System weryfikuje status – jeśli wynosi NEW, zmienia go na CANCELLED i tworzy wpis w tabeli ANULOWANIE.
- Warunek poprawności: Zmiana statusu na CANCELLED i uniemożliwienie przyjęcia zlecenia przez technika.
- Sytuacja błędna: Zlecenie posiada status DELIVERED lub wyższy -> odmowa anulowania.

## Cykl 2:

## **Cel i Granice Wersji v2**:

Umożliwienie technikowi serwisu wprowadzania wyników diagnozy i sporządzania kosztorysu, umożliwienie klientowi akceptacji lub odrzucenia wyceny online, oraz zautomatyzowanie zamawiania brakujących części z hurtowni zewnętrznej.

## **Opis efektu wersji v2 dla Użytkownika**:

Po fizycznym dostarczeniu sprzętu technik w panelu serwisu przeprowadza diagnozę i wprowadza kosztorys. Klient otrzymuje możliwość wglądu do wyceny na stronie WWW i podejmuje decyzję o jej akceptacji lub odrzuceniu. Jeśli naprawa wymaga komponentów, których nie ma na stanie w magazynie, system automatycznie wysyła zamówienie do zewnętrznej hurtowni i aktualizuje status zlecenia.

# Widoki (W)

- W04 (aktualizacja): Status Zlecenia i Akceptacja Kosztorysu
- W06: Panel Technika – Diagnoza i Kosztorys
- W07: Panel Technika – Przypisanie i Zamówienie Części

# Baza Danych (B)

- B07: TECHNIK: id (PK, int), imie (varchar), nazwisko (varchar).
- B08: KOSZTORYS: id (PK, int), kwota (decimal), status_akceptacji (varchar: OCZEKUJE, AKCEPTOWANY, ODRZUCONY), zlecenie_id (FK -> ZLECENIE.id, UQ).
- B09: NAPRAWA: id (PK, int), opis (text), czas_naprawy (int), zlecenie_id (FK -> ZLECENIE.id, UQ), technik_id (FK -> TECHNIK.id).
- B10: CZESC: id (PK, int), nazwa (varchar), cena (decimal), dostepnosc (int).
- B11: ZLECENIE_CZESC: zlecenie_id (FK -> ZLECENIE.id), czesc_id (FK -> CZESC.id), ilosc (int), status_zamowienia (varchar: REZERWACJA, ZAMOWIONE_HURTOWNIA, DOSTARCZONE).
- ZLECENIE (rozszerzenie pola status z B05): rozbudowa o nowe stany: IN_PROGRESS, WAITING_FOR_PARTS, COMPLETED.

# Funkcjonalność (F)

### F05: Wprowadzenie diagnozy i przygotowanie kosztorysu

- Aktor: Technik
- Powiązany widok: W06
- Potrzebne dane: B05, B07, B08, B09
- Oczekiwane działanie: Technik uzupełnia opis diagnozy i wprowadza kwotę kosztorysu. System zmienia status zlecenia na IN_PROGRESS, tworzy rekord KOSZTORYS ze stanem OCZEKUJE i udostępnia go klientowi.
- Warunek poprawności: Zlecenie w stanie DELIVERED, kwota kosztorysu większa od 0.
- Sytuacja błędna: Próba utworzenia kosztorysu dla zlecenia o statusie CANCELLED lub niedostarczonego.

### F06: Decyzja klienta w sprawie kosztorysu (Online)

- Aktor: Klient
- Powiązany widok: W04
- Potrzebne dane: B05, B08
- Oczekiwane działanie: Klient przegląda kosztorys w W04 i klika "Akceptuj" lub "Odrzuć". W przypadku akceptacji status wyceny zmienia się na AKCEPTOWANY. W przypadku odrzucenia naprawa zostaje zaniechana, a status zlecenia przechodzi w COMPLETED.
- Warunek poprawności: Status zlecenia wynosi IN_PROGRESS, a status_akceptacji wyceny wynosi OCZEKUJE.
- Sytuacja błędna: Próba zmiany decyzji po zatwierdzeniu lub odrzuceniu wyceny.

### F07: Weryfikacja stanów magazynowych i zamówienie części z hurtowni

- Aktor: Technik, System (Hurtownia - Zewnętrzne API)
- Powiązany widok: W07
- Potrzebne dane: B05, B10, B11
- Oczekiwane działanie: Technik przypisuje część do naprawy. System weryfikuje pole dostepnosc w tabeli CZESC. W przypadku braku na stanie system zmienia status zlecenia na WAITING_FOR_PARTS i automatycznie wysyła zamówienie przez API do hurtowni zewnętrznej.
- Warunek poprawności: Kosztorys został wcześniej zaakceptowany przez klienta (status AKCEPTOWANY).
- Sytuacja błędna: Błąd komunikacji z zewnętrznym API hurtowni -> zapisanie stanu oczekiwania na ponownienie transmisji i komunikat błędu dla technika.


## Cykl 3:

## **Cel i Granice Wersji v3**:
Obsługa finalnego procesu rozliczenia finansowego (płatności, zwroty i rekompensaty) oraz zamknięcie i archiwizacja zlecenia w serwisie.
## **Opis efektu wersji v3 dla Użytkownika**:
Klient po zakończeniu naprawy stawia się w serwisie po odbiór urządzenia, dokonuje płatności lub – w przypadku uszkodzenia sprzętu przez serwis – otrzymuje rekompensatę finansową. Zlecenie zostaje formalnie zamknięte i zarchiwizowane przez technika w systemie.

# Widoki (W)

- W08: Panel Kasowy / Wydanie Sprzętu i Płatności

# Baza Danych (B)

- B12: PLATNOSC: id (PK, int), kwota (decimal), status (varchar), data_platnosci (datetime), zlecenie_id (FK -> ZLECENIE.id, UQ).
- B13: ZWROT: id (PK, int), kwota (decimal), powod (varchar), typ_zwrotu (varchar), platnosc_id (FK -> PLATNOSC.id).
- ZLECENIE (rozszerzenie pola status z B05): rozbudowa o stan zamknięcia/archiwizacji.

# Funkcjonalność (F)

### F08: Rejestracja płatności i wydanie sprzętu (Zamknięcie zlecenia)

- Aktor: Technik, Klient
- Powiązany widok: W08
- Potrzebne dane: B05, B12, B13
- Oczekiwane działanie: Klient dokonuje płatności za usługę w kasie serwisu. System rejestruje wpłatę w tabeli PLATNOSC, zamyka zlecenie i archiwizuje dane, po czym technik wydaje sprzęt klientowi.
- Warunek poprawności: Zlecenie w stanie COMPLETED, uregulowana pełna kwota kosztorysu.
- Sytuacja błędna: W przypadku uszkodzenia sprzętu przez serwis, system rejestruje opcjonalny zwrot/rekompensatę w tabeli ZWROT przed ostatecznym rozliczeniem i zamknięciem.
