1. Wybór Technologii

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
