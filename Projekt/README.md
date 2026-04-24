# Monitorowanie Wydatków Domowych

System monitorowania wydatków domowych zbudowany w Django z wykorzystaniem wzorca architektonicznego MVC.

## Spis treści
- [Funkcjonalności](#funkcjonalności)
- [Technologie](#technologie)
- [Instalacja](#instalacja)
- [Uruchomienie przez Docker](#uruchomienie-przez-docker)
- [Sposób użycia](#sposób-użycia)
- [Struktura projektu](#struktura-projektu-mvc)
- [Testy](#testy)

## Funkcjonalności

| Funkcja | Opis |
|---|---|
| **Autentykacja użytkowników** | Rejestracja, logowanie, wylogowanie — każdy użytkownik widzi tylko swoje dane |
| **Wydatki** | Dodawanie, edycja, usuwanie wydatków z tytułem, kwotą, datą, kategorią i opisem |
| **Kategorie** | Własne kategorie z wyborem koloru |
| **Budżety** | Miesięczne limity budżetowe per kategoria z paskiem postępu |
| **Panel główny** | Przegląd ze statystykami, wykres kołowy wg kategorii, wykres słupkowy za ostatnie 6 miesięcy |
| **Wyszukiwanie i filtrowanie** | Filtrowanie wydatków po tytule, kategorii, zakresie dat; sortowanie po dacie/kwocie/tytule |
| **Kursy walut** | Aktualne kursy z API NBP + kalkulator PLN do dowolnej waluty |
| **Zmiana waluty** | Przełączanie wyświetlanej waluty (PLN / EUR / USD / GBP) dla całej aplikacji |
| **Wielojęzyczność** | Interfejs w języku polskim i angielskim (i18n) |
| **Walidacja** | Walidacja formularzy po stronie serwera i klienta |
| **Panel admina** | Django admin dla wszystkich modeli |

## Technologie

- **Python 3.13** + **Django 6.0**
- **Bootstrap 5.3** — responsywny interfejs
- **Chart.js** — interaktywne wykresy
- **Bootstrap Icons** — biblioteka ikon
- **SQLite** — baza danych
- **API NBP** — aktualne kursy walut (bez klucza API)
- **Docker** — konteneryzacja

## Instalacja

### Wymagania
- Python 3.10+
- pip

### Kroki

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/pythofree/LabMVC.git
cd LabMVC/Projekt

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Wykonaj migracje bazy danych
python manage.py migrate

# 4. Uruchom serwer
python manage.py runserver
```

Otwórz przeglądarkę pod adresem **http://127.0.0.1:8000**

Zarejestruj konto i zacznij śledzić swoje wydatki!

## Uruchomienie przez Docker

```bash
# Zbuduj i uruchom
docker-compose up --build

# Otwórz http://localhost:8000
```

## Sposób użycia

1. **Rejestracja** — utwórz konto pod adresem `/register/`
2. **Kategorie** — przejdź do Kategorie i dodaj kategorie wydatków (np. Jedzenie, Transport)
3. **Budżety** — ustaw miesięczne limity dla każdej kategorii
4. **Wydatki** — dodawaj codzienne wydatki
5. **Panel główny** — przeglądaj wykresy i statystyki
6. **Waluty** — sprawdzaj aktualne kursy i przeliczaj PLN na inne waluty

## Struktura projektu (MVC)

```
Projekt/
├── expense_tracker/        # Projekt Django (settings, urls)
├── expenses/               # Główna aplikacja
│   ├── models.py           # MODEL — Category, Expense, Budget
│   ├── views.py            # KONTROLER — cała logika obsługi żądań
│   ├── forms.py            # Walidacja formularzy
│   ├── urls.py             # Routing URL
│   ├── admin.py            # Konfiguracja panelu admina
│   ├── tests.py            # Testy jednostkowe (17 testów)
│   └── templates/expenses/ # WIDOK — wszystkie szablony HTML
├── locale/                 # Tłumaczenia (PL/EN)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Modele

- **Category** — nazwa, kolor, użytkownik (FK)
- **Expense** — tytuł, kwota, data, kategoria (FK), opis, użytkownik (FK)
- **Budget** — kategoria (FK), limit_miesięczny, miesiąc, rok, użytkownik (FK)

## Testy

```bash
python manage.py test expenses
```

Uruchamia 17 testów jednostkowych pokrywających modele, widoki i autentykację.
