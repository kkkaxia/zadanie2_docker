#KLUCZ API - 31c59dd39bfbd8e0db669ff800577f7e

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import logging
import datetime
import requests
import os

app = FastAPI()

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zadanie1")

# Stałe
AUTHOR_NAME = "Kateryna Zinchuk"  
PORT = int(os.getenv("PORT", 8000))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "brak-klucza")

# Lista krajów i miast (rozbudowana)
cities = {
    "Polska": ["Warszawa", "Kraków", "Gdańsk"],
    "Niemcy": ["Berlin", "Monachium", "Hamburg"],
    "Francja": ["Paryż", "Marsylia", "Lyon"],
    "USA": ["Nowy Jork", "Los Angeles", "Chicago"],
    "Japonia": ["Tokio", "Osaka", "Kioto"]
}

# Logowanie przy starcie
@app.on_event("startup")
def startup_event():
    logger.info(f"Data uruchomienia: {datetime.datetime.now()}")
    logger.info(f"Autor: {AUTHOR_NAME}")
    logger.info(f"Nasłuch na porcie: {PORT}")

# Strona główna (formularz wyboru kraju)
@app.get("/", response_class=HTMLResponse)
def read_root():
    form_html = """
    <h2>Wybierz kraj:</h2>
    <form action="/select_city" method="post">
    """
    for country in cities.keys():
        form_html += f'<input type="radio" name="country" value="{country}">{country}<br>'
    form_html += """
        <input type="submit" value="Wybierz kraj">
    </form>
    """
    return form_html

# Strona wyboru miasta po wybraniu kraju
@app.post("/select_city", response_class=HTMLResponse)
def select_city(country: str = Form(...)):
    city_options = cities.get(country)
    if not city_options:
        return f"<h3>Nieznany kraj: {country}</h3>"

    form_html = f"""
    <h2>Wybierz miasto w kraju {country}:</h2>
    <form action="/weather" method="post">
        <input type="hidden" name="country" value="{country}">
    """
    for city in city_options:
        form_html += f'<input type="radio" name="city" value="{city}">{city}<br>'
    form_html += """
        <input type="submit" value="Pokaż pogodę">
    </form>
    """
    return form_html

# Pokazanie pogody
@app.post("/weather", response_class=HTMLResponse)
def get_weather(country: str = Form(...), city: str = Form(...)):
    if OPENWEATHER_API_KEY == "brak-klucza":
        return "<h3>Brak klucza API do pobrania pogody!</h3>"

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pl"
    response = requests.get(weather_url)
    if response.status_code != 200:
        return "<h3>Nie udało się pobrać pogody</h3>"

    data = response.json()
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    return f"<h2>Pogoda w {city} ({country}):</h2><p>Temperatura: {temp}°C</p><p>Opis: {description}</p>"
