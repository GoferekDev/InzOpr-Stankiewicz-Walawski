1. Test po prompcie 1.
po wejściu na panel technika ze strony głównej:
sqlite3.OperationalError: no such column: k.nazwiskootc

Naprawa sugerowana przez AI:


Ten błąd wynika z literówki w zapytaniu SQL w funkcji `w05_tech` w pliku `app.py`. W zapytaniu omyłkowo wpisano nieistniejącą kolumnę `nazwiskootc` zamiast `nazwisko`.

### Jak to naprawić?

Otwórz plik `app.py`, znajdź funkcję `w05_tech` (około linii 140) i popraw linijkę z zapytaniem SQL z:

```python
    cursor.execute("""
        SELECT z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwiskootc AS nazwisko 
        FROM zlecenie z 
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
    """)

```

na poprawną wersję:

```python
    cursor.execute("""
        SELECT z.numer, z.status, u.typ_sprzetu, u.model, k.imie, k.nazwisko AS nazwisko 
        FROM zlecenie z 
        JOIN urzadzenie u ON z.urzadzenie_id = u.id
        JOIN formularz_zgloszenia f ON z.formularz_id = f.id
        JOIN klient k ON f.klient_id = k.id
    """)

```

### Cała poprawiona funkcja `w05_tech`:

```python
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

```

Po zapisaniu pliku `app.py` zrestartuj serwer Flask (zatrzymaj go przez `Ctrl+C` i uruchom ponownie `python app.py`), a błąd zniknie.
