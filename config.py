import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITIES_FILE = "cities.json"
TIMES_FILE = "times.json"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в переменных окружения/.env")
if not WEATHER_API_KEY:
    raise RuntimeError("WEATHER_API_KEY не найден в переменных окружения/.env")
