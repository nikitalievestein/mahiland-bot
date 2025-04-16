import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, DAY_DURATION
from game_data import game_state, save_game_state
from handlers import setup_handlers

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
setup_handlers(dp)

# Функция для обновления игрового времени
async def update_game_time():
    while True:
        for user_id in game_state:
            state = game_state[user_id]
            state["days_passed"] += 1

            # Обновляем бюджет: налоги минус расходы
            taxes = state["gdp"] * (state["tax_rate"] / 100)
            expenses = state["army_funding"] + state["maintenance_cost"]
            state["budget"] += taxes - expenses

            # Случайное событие (10% шанс)
            if random.random() < 0.1:
                event = random.choice([
                    ("Урожай удался!", 0.05, -5),  # +5% GDP, -5% недовольства
                    ("Экономический кризис!", -0.1, 10),  # -10% GDP, +10% недовольства
                    ("Протесты в городах!", 0, 15)  # +15% недовольства
                ])
                event_name, gdp_change, diss_change = event
                state["gdp"] *= (1 + gdp_change)
                state["dissatisfaction"] += diss_change
                await bot.send_message(user_id, f"Событие: {event_name}\nGDP: €{state['gdp']:,.0f}\nНедовольство: {state['dissatisfaction']}%")

            # Проверка выборов (каждые 4 года)
            if state["days_passed"] % (4 * 365) == 0:
                if state["dissatisfaction"] > 50:
                    await bot.send_message(user_id, "Вы проиграли выборы! Игра окончена. Начните заново с /start")
                    del game_state[user_id]
                else:
                    await bot.send_message(user_id, "Вы выиграли выборы! Продолжайте править!")

            # Проверка переворота
            if state["dissatisfaction"] >= 80:
                await bot.send_message(user_id, "Народ сверг вас! Игра окончена. Начните заново с /start")
                del game_state[user_id]

            await save_game_state()

        await asyncio.sleep(DAY_DURATION)

# Запуск бота
async def main():
    print("Mahiland Bot запущен!")
    asyncio.create_task(update_game_time())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())