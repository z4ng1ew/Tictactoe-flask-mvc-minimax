# Импортируем классы из слоёв
from domain.service.impl import GameServiceImpl
from datasource.storage import GameStorage
from datasource.repository.game_repo import GameRepository
from web.route.controller import create_game_controller

# Точка входа: выполняется, когда запускаешь `python main.py`
if __name__ == "__main__":
    # 1. Создаём хранилище (память)
    storage = GameStorage()
    # 2. Создаём репозиторий, передаём хранилище (внедрение зависимостей)
    repo = GameRepository(storage)
    # 3. Создаём сервис, передаём репозиторий
    service = GameServiceImpl(repo)
    # 4. Создаём Flask-приложение, передаём сервис
    app = create_game_controller(service)
    
    # Запускаем сервер на порту 5000
    # debug=True — автоматическая перезагрузка при изменении кода (только для разработки!)
    app.run(host='0.0.0.0', port=5000, debug=True)