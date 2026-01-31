import json
import os
from typing import Dict, List

import requests

from config import CITIES_FILE, WEATHER_API_KEY, TIMES_FILE


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cities() -> Dict[str, List[str]]:
    return _load_json(CITIES_FILE)


def save_cities(data: Dict[str, List[str]]) -> None:
    _save_json(CITIES_FILE, data)


def load_times() -> Dict[str, List[str]]:
    return _load_json(TIMES_FILE)


def save_times(data: Dict[str, List[str]]) -> None:
    _save_json(TIMES_FILE, data)



def get_weather(city: str) -> str:
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params=params,
            timeout=5,
        )
    except Exception:
        return f"{city}: ошибка запроса"

    if r.status_code != 200:
        return f"{city}: ошибка ({r.status_code})"

    data = r.json()
    try:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{city}: {temp:.1f}°C, {desc.capitalize()}"
    except Exception:
        return f"{city}: неверный ответ API"
