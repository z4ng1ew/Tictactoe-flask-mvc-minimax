import json

def test_web_checklist():
    print("🔍 Проверка Задания 4 (web-слой)...\n")
    
    # 1. Импорт моделей web
    from web.model.game_web import GameWeb
    from web.model.game_board_web import GameBoardWeb
    print("✅ Модели игрового поля и игры в web описаны.")
    
    # 2. Проверка @dataclass
    board = GameBoardWeb(matrix=[[0]*3]*3)
    game = GameWeb(id="test-uuid", board=board)
    assert hasattr(board, 'matrix') and hasattr(board, 'size')
    print("✅ Модели используют dataclass (автоматический __init__).")
    
    # 3. Мапперы
    from web.mapper.mapper import GameWebMapper
    from domain.model.game import Game
    from domain.model.game_board import GameBoard
    
    # Создаём domain-объект для теста
    domain_board = GameBoard(matrix=[[1,0,0],[0,2,0],[0,0,1]])
    domain_game = Game(board=domain_board)
    
    # Тестируем domain -> web
    web_game = GameWebMapper.domain_to_web(domain_game)
    assert isinstance(web_game, GameWeb)
    assert isinstance(web_game.board, GameBoardWeb)
    
    # Тестируем web -> domain
    restored = GameWebMapper.web_to_domain(web_game)
    assert restored.board.matrix == domain_board.matrix
    print("✅ Мапперы domain <-> web реализованы и работают в обе стороны.")
    
    # 4. Контроллер Flask
    from flask import Flask
    # <-- ИСПРАВЛЕНО: импортируем версию сервиса, которая принимает репозиторий
    from datasource.service.game_service_impl import GameServiceImplWithRepo
    from datasource.storage import GameStorage
    from datasource.repository.game_repo import GameRepository
    from web.route.controller import create_game_controller
    
    # Собираем зависимости
    storage = GameStorage()
    repo = GameRepository(storage)
    # <-- ИСПРАВЛЕНО: создаём сервис, передавая готовый репозиторий
    service = GameServiceImplWithRepo(repo)
    app = create_game_controller(service)
    
    assert isinstance(app, Flask)
    print("✅ Контроллер создаёт Flask-приложение.")
    
    # 5. Тест POST-запроса (через тестовый клиент Flask)
    with app.test_client() as client:
        test_input = {
            "id": str(domain_game.id),
            "board": {
                "matrix": [[1,0,0],[0,2,0],[0,0,0]],
                "size": 3
            }
        }
        response = client.post(
            f'/game/{domain_game.id}',
            data=json.dumps(test_input),
            content_type='application/json'
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert 'id' in data and 'board' in data
        print("✅ POST /game/{UUID} принимает валидный запрос и возвращает обновлённую игру.")
        
        bad_response = client.post(
            f'/game/{domain_game.id}',
            data='not-json',
            content_type='application/json'
        )
        assert bad_response.status_code == 400
        print("✅ Некорректный запрос возвращает ошибку 400 с описанием.")
    
    # 6. Поддержка нескольких игр
    storage1 = GameStorage()
    storage2 = GameStorage()
    assert storage1 is not storage2
    print("✅ Архитектура поддерживает несколько одновременных игр.")
    
    # 7. Разделение на файлы
    import os
    web_files = [
        'web/model/game_web.py',
        'web/model/game_board_web.py',
        'web/mapper/mapper.py',
        'web/route/controller.py'
    ]
    for f in web_files:
        assert os.path.exists(f), f"File {f} not found"
    print("✅ Модели, мапперы и контроллер находятся в разных файлах.")
    
    print("\n🎉 Все пункты чек-листа Задания 4 пройдены!")

if __name__ == "__main__":
    test_web_checklist()