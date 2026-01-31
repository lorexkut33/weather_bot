from aiogram import Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from utils import load_cities, save_cities, load_times, save_times, get_weather


async def cmd_start(message: Message):
    await message.answer(
        "🌤 Погодный бот.\n"
        "Команды:\n"
        "/setcities <города> — задать города\n"
        "/cities — показать города\n"
        "/settime <HH:MM ...> — задать время(ена) рассылки\n"
        "/times — показать время\n"
        "/weather — показать погоду сейчас"
    )


async def cmd_setcities(message: Message, bot: Bot):
    # В личке не проверяем админа, в группе проверяем
    if message.chat.type != "private":
        admins = [adm.user.id for adm in await bot.get_chat_administrators(message.chat.id)]
        if message.from_user.id not in admins:
            return await message.answer(" Только админы группы могут настраивать города.")

    parts = message.text.split(maxsplit=1)
    data = load_cities()
    key = str(message.chat.id)

    if len(parts) == 1:
        current = data.get(key, [])
        text = ", ".join(current) if current else "нет городов"
        return await message.answer(
            f"Текущие города: {text}\n"
            "Пример: /setcities Москва"
        )

    cities_list = parts[1].split()
    data[key] = cities_list
    save_cities(data)
    await message.answer("✅ Города обновлены: " + ", ".join(cities_list))


async def cmd_cities(message: Message):
    data = load_cities()
    current = data.get(str(message.chat.id), [])
    text = ", ".join(current) if current else "нет городов"
    await message.answer(f"Города для этого чата: {text}")


async def cmd_settime(message: Message, bot: Bot):
    # В личке не проверяем админа
    if message.chat.type != "private":
        admins = [adm.user.id for adm in await bot.get_chat_administrators(message.chat.id)]
        if message.from_user.id not in admins:
            return await message.answer("Только админы группы могут настраивать время.")

    parts = message.text.split(maxsplit=1)
    data = load_times()
    key = str(message.chat.id)

    if len(parts) == 1:
        current = data.get(key, [])
        text = ", ".join(current) if current else "по умолчанию 09:00"
        return await message.answer(
            f"Текущее время рассылок: {text}\n"
            "Пример: /settime 09:00 21:30"
        )

    # простая валидация ч:М
    raw_times = parts[1].split()
    valid_times = []

    for t in raw_times:
        # допускаем форматы "6:00", "06:00", "18:0", "18:00"
        if ":" not in t:
            continue
        h_str, m_str = t.split(":", maxsplit=1)
        if not (h_str.isdigit() and m_str.isdigit()):
            continue
        h, m = int(h_str), int(m_str)
        if 0 <= h < 24 and 0 <= m < 60:
            valid_times.append(f"{h:02d}:{m:02d}")  # нормализуем к 06:00, 18:00

    if not valid_times:
        return await message.answer(
            "Неверный формат. Используй HH:MM, например: /settime 6:00 18:00"
        )

    data[key] = valid_times
    save_times(data)
    await message.answer(" Время рассылок обновлено: " + ", ".join(valid_times))


async def cmd_times(message: Message):
    data = load_times()
    current = data.get(str(message.chat.id), [])
    text = ", ".join(current) if current else "по умолчанию 09:00"
    await message.answer(f"Время рассылок для этого чата: {text}")


async def cmd_weather(message: Message):
    data = load_cities()
    key = str(message.chat.id)
    cities = data.get(key, [])

    # Разбираем аргументы: /weather [город...]
    parts = message.text.split(maxsplit=1)

    # Если город не указан → показываем все
    if len(parts) == 1:
        if not cities:
            return await message.answer(
                "Города не настроены.\n"
                "Используй /setcities Москва Наро-Фоминск"
            )
        lines = [get_weather(city) for city in cities]
        text = "🌤 Текущая погода по всем городам:\n" + "\n".join(lines)
        return await message.answer(text)

    # Если город указан
    query_city = parts[1].strip()

    # Пытаемся найти точное совпадение среди сохранённых
    if query_city not in cities:
        return await message.answer(
            "Такой город не найден в списке.\n"
            "У тебя сейчас: " + (", ".join(cities) if cities else "пусто")
        )

    weather_text = get_weather(query_city)
    await message.answer(f"🌤 Погода в выбранном городе:\n{weather_text}")
