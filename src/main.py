# Импортируем классы из слоёв
from datasource.storage import GameStorage
from datasource.repository.game_repo import GameRepository
# <-- ИСПРАВЛЕНО: берём реализацию сервиса с репозиторием из datasource
from datasource.service.game_service_impl import GameServiceImplWithRepo
from web.route.controller import create_game_controller

# Точка входа: выполняется, когда запускаешь `python main.py`
if __name__ == "__main__":
    # 1. Создаём хранилище (память)
    storage = GameStorage()
    # 2. Создаём репозиторий, передаём хранилище (внедрение зависимостей)
    repo = GameRepository(storage)
    # <-- ИСПРАВЛЕНО: используем класс, который умеет принимать репозиторий
    service = GameServiceImplWithRepo(repo)
    # 3. Создаём Flask-приложение, передаём сервис
    app = create_game_controller(service)
    
    # Запускаем сервер на порту 5000
    # debug=True — автоматическая перезагрузка при изменении кода (только для разработки!)
    app.run(host='0.0.0.0', port=5000, debug=True)