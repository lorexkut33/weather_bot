import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
import aioschedule

from config import BOT_TOKEN
from handlers import (
    cmd_start, cmd_setcities, cmd_cities,
    cmd_settime, cmd_times, cmd_weather,
)
from utils import load_cities, load_times, get_weather


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.register(cmd_start, CommandStart())
dp.message.register(cmd_setcities, Command("setcities"))
dp.message.register(cmd_cities, Command("cities"))
dp.message.register(cmd_settime, Command("settime"))
dp.message.register(cmd_times, Command("times"))
dp.message.register(cmd_weather, Command("weather"))


async def send_report_for_chat(chat_id: int, cities: list, label: str):
    lines = [get_weather(city) for city in cities]
    text = f"🌤 Погодный отчёт ({label}):\n" + "\n".join(lines)
    try:
        await bot.send_message(chat_id, text)
    except Exception as e:
        logging.warning("Не удалось отправить в %s: %s", chat_id, e)


async def scheduler_loop():
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        cities_data = load_cities()
        times_data = load_times()

        for chat_id_str, cities in cities_data.items():
            if not cities:
                continue

            # список времён для этого чата
            times_list = times_data.get(chat_id_str)
            if not times_list:
                times_list = ["09:00"]  # дефолт

            if current_time in times_list:
                await send_report_for_chat(int(chat_id_str), cities, current_time)

        await asyncio.sleep(60)  # проверяем раз в минуту


async def main():
    asyncio.create_task(scheduler_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
