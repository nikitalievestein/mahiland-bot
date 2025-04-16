import json

# Хранилище состояния игры
game_state = {}

# Сохранение состояния в JSON
def save_game_state():
    with open("game_data.json", "w") as f:
        json.dump(game_state, f, indent=4)

# Загрузка состояния из JSON
def load_game_state():
    try:
        with open("game_data.json", "r") as f:
            global game_state
            game_state.update(json.load(f))
    except FileNotFoundError:
        pass