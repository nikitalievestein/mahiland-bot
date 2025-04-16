from aiogram import Dispatcher, types
from aiogram.filters import Command
from game_data import game_state, save_game_state

def setup_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        user_id = message.from_user.id
        if user_id in game_state:
            await message.answer("Вы уже правите Mahiland! Проверьте статус с /stats")
            return

        kb = [
            [types.KeyboardButton(text="Народная партия"), types.KeyboardButton(text="Либеральная партия")]
        ]
        markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Добро пожаловать в Mahiland! Вы президент. Выберите партию:", reply_markup=markup)

    @dp.message(lambda message: message.text in ["Народная партия", "Либеральная партия"])
    async def choose_party(message: types.Message):
        user_id = message.from_user.id
        party = message.text
        game_state[user_id] = {
            "gdp": 100_000_000_000,  # €100B
            "budget": 10_000_000_000,  # €10B
            "population": 2_500_000,
            "dissatisfaction": 20,
            "army_funding": 0,
            "army_type": None,
            "party": party,
            "tax_rate": 20,
            "days_passed": 0,
            "infrastructure": {},
            "maintenance_cost": 0
        }
        if party == "Либеральная партия":
            game_state[user_id]["gdp"] *= 1.1  # +10% GDP
            game_state[user_id]["dissatisfaction"] += 5  # +5% недовольства
        else:
            game_state[user_id]["dissatisfaction"] -= 5  # -5% недовольства

        await message.answer(
            f"Вы выбрали {party}! Теперь вы президент Mahiland.\n"
            "Команды:\n/stats - Статус страны\n/economy - Экономика\n/army - Армия\n/infrastructure - Постройки\n/population - Население",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await save_game_state()

    @dp.message(Command("stats"))
    async def cmd_stats(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        report = (
            f"📊 Статус Mahiland 📊\n"
            f"Партия: {state['party']}\n"
            f"Дней у власти: {state['days_passed']}\n"
            f"GDP: €{state['gdp']:,.0f}\n"
            f"Бюджет: €{state['budget']:,.0f}\n"
            f"Население: {state['population']:,}\n"
            f"Недовольство: {state['dissatisfaction']}%\n"
            f"Армия: {state['army_type'] or 'Не выбрана'}\n"
            f"Налоги: {state['tax_rate']}%"
        )
        await message.answer(report)
        await save_game_state()

    @dp.message(Command("economy"))
    async def cmd_economy(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        kb = [
            [types.KeyboardButton(text="Повысить налоги"), types.KeyboardButton(text="Понизить налоги")],
            [types.KeyboardButton(text="Назад")]
        ]
        markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            f"Экономика:\nGDP: €{state['gdp']:,.0f}\nБюджет: €{state['budget']:,.0f}\nНалоги: {state['tax_rate']}%",
            reply_markup=markup
        )

    @dp.message(lambda message: message.text in ["Повысить налоги", "Понизить налоги"])
    async def adjust_taxes(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        if message.text == "Повысить налоги":
            state["tax_rate"] += 5
            state["dissatisfaction"] += 10
            await message.answer(f"Налоги повышены до {state['tax_rate']}%! Недовольство: {state['dissatisfaction']}%")
        else:
            state["tax_rate"] = max(5, state["tax_rate"] - 5)
            state["dissatisfaction"] -= 5
            await message.answer(f"Налоги понижены до {state['tax_rate']}%! Недовольство: {state['dissatisfaction']}%")
        await save_game_state()

    @dp.message(Command("army"))
    async def cmd_army(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        if not state["army_type"]:
            kb = [
                [types.KeyboardButton(text="Профессиональная"), types.KeyboardButton(text="Призывная")]
            ]
            markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(
                "Выберите тип армии:\n"
                "- Профессиональная: дорогая, но сильная\n"
                "- Призывная: дешевая, но слабая",
                reply_markup=markup
            )
        else:
            await message.answer(
                f"Ваша армия: {state['army_type']}\nФинансирование: €{state['army_funding']:,.0f}",
                reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Назад")]])
            )

    @dp.message(lambda message: message.text in ["Профессиональная", "Призывная"])
    async def set_army_type(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        state["army_type"] = message.text
        state["army_funding"] = 500_000_000 if message.text == "Профессиональная" else 100_000_000
        await message.answer(
            f"Армия установлена: {state['army_type']}!\nФинансирование: €{state['army_funding']:,.0f}",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await save_game_state()

    @dp.message(Command("infrastructure"))
    async def cmd_infrastructure(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        projects = {
            "Госпиталь": {"cost": 2_000_000_000, "effect": "Недовольство -10%", "dissatisfaction": -10},
            "Дороги": {"cost": 1_500_000_000, "effect": "GDP +5%", "gdp": 0.05},
            "Школа": {"cost": 1_000_000_000, "effect": "Недовольство -5%", "dissatisfaction": -5}
        }
        kb = [[types.KeyboardButton(text=f"Построить {name}")] for name in projects]
        kb.append([types.KeyboardButton(text="Назад")])
        markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        projects_list = "\n".join(f"- {name}: €{data['cost']:,.0f} ({data['effect']})" for name, data in projects.items())
        await message.answer(
            f"Инфраструктура:\nБюджет: €{state['budget']:,.0f}\nПроекты:\n{projects_list}",
            reply_markup=markup
        )

    @dp.message(lambda message: message.text.startswith("Построить "))
    async def build_project(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        project_name = message.text.replace("Построить ", "")
        projects = {
            "Госпиталь": {"cost": 2_000_000_000, "effect": "Недовольство -10%", "dissatisfaction": -10},
            "Дороги": {"cost": 1_500_000_000, "effect": "GDP +5%", "gdp": 0.05},
            "Школа": {"cost": 1_000_000_000, "effect": "Недовольство -5%", "dissatisfaction": -5}
        }
        if project_name not in projects:
            await message.answer("Такого проекта нет!")
            return

        project = projects[project_name]
        if state["budget"] < project["cost"]:
            await message.answer(f"Недостаточно денег! Нужно €{project['cost']:,.0f}")
            return

        state["budget"] -= project["cost"]
        state["maintenance_cost"] += project["cost"] * 0.01
        if "dissatisfaction" in project:
            state["dissatisfaction"] = max(0, state["dissatisfaction"] + project["dissatisfaction"])
        if "gdp" in project:
            state["gdp"] *= (1 + project["gdp"])
        state["infrastructure"][project_name] = state["infrastructure"].get(project_name, 0) + 1

        await message.answer(
            f"{project_name} построен!\nБюджет: €{state['budget']:,.0f}\nЭффект: {project['effect']}"
        )
        await save_game_state()

    @dp.message(Command("population"))
    async def cmd_population(message: types.Message):
        user_id = message.from_user.id
        if user_id not in game_state:
            await message.answer("Начните игру с /start!")
            return

        state = game_state[user_id]
        population_change = random.randint(-1000, 2000)
        state["population"] += population_change
        await message.answer(
            f"Население: {state['population']:,}\n"
            f"Изменение: {population_change:+,}\n"
            f"Недовольство: {state['dissatisfaction']}%"
        )
        await save_game_state()

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(
            "Mahiland — игра, где вы президент страны!\n"
            "Команды:\n"
            "/start - Начать игру\n"
            "/stats - Статус страны\n"
            "/economy - Управлять экономикой\n"
            "/army - Настроить армию\n"
            "/infrastructure - Строить здания\n"
            "/population - Проверить население\n"
            "/help - Показать это сообщение"
        )

    @dp.message(lambda message: message.text == "Назад")
    async def go_back(message: types.Message):
        await message.answer("Выберите команду:", reply_markup=types.ReplyKeyboardRemove())