# Импортируем Flask — основной класс фреймворка
from flask import Flask, request, jsonify, abort, send_from_directory
# Импортируем тип для аннотаций
from typing import Tuple
# Импортируем бизнес-интерфейс (контракт)
from domain.service.interface import GameServiceInterface
# Импортируем маппер для перевода между слоями
from web.mapper.mapper import GameWebMapper
# Импортируем web-модель для ответа
from web.model.game_web import GameWeb
# Импортируем os для работы с путями
import os

def create_game_controller(service: GameServiceInterface) -> Flask:
    """
    Создаёт Flask-приложение с маршрутами для игры.
    :param service: объект, реализующий GameServiceInterface
    :return: настроенный объект Flask
    """
    app = Flask(__name__)

    # =========================================================
    # 🎮 НОВЫЙ МАРШРУТ: Главная страница с веб-интерфейсом
    # =========================================================
    @app.route('/')
    def serve_frontend():
        """Отдаёт HTML-страницу для игры в браузере."""
        # Путь к папке static: web/route/../../static = web/static/
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        return send_from_directory(static_dir, 'index.html')
    
    # =========================================================
    # 📦 Маршрут для раздачи статики (CSS/JS, если вынесешь)
    # =========================================================
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        return send_from_directory(static_dir, filename)

    # =========================================================
    # 🎯 СУЩЕСТВУЮЩИЙ МАРШРУТ: API для ходов (не меняем!)
    # =========================================================
    @app.route('/game/<string:game_id>', methods=['POST'])
    def handle_game_move(game_id: str):
        """
        Обработчик хода: принимает ход игрока, возвращает ход компьютера.
        """
        data = request.get_json()
        
        # 1. Валидация структуры запроса
        if not data or not isinstance(data, dict):
            abort(400, description="Request body must be a valid JSON object")
        
        try:
            # 2. Парсинг в web-модель
            web_game_input = GameWeb(**data)
            # 3. Перевод в domain-модель
            domain_game = GameWebMapper.web_to_domain(web_game_input)
        except (KeyError, ValueError, TypeError) as e:
            abort(400, description=f"Invalid game  {str(e)}")
        
        # =========================================================
        # 🔥 Валидация через репозиторий
        # =========================================================
        previous_board = service.get_previous_board(domain_game.id)
        if previous_board is not None:
            if not service.validate_board(domain_game, previous_board):
                abort(400, description="Board validation failed: previous moves were modified")
        
        # 4. Получаем следующий ход от алгоритма
        next_move: Tuple[int, int] = service.get_next_move(domain_game)
        
        # 5. Применяем ход компьютера
        domain_game.board.matrix[next_move[0]][next_move[1]] = 2
        
        # 6. Проверяем окончание игры
        if service.is_game_over(domain_game):
            pass
        
        # 🔥 Сохраняем обновлённое состояние
        service.save_game_state(domain_game)
        
        # 7. Переводим результат обратно в web-модель
        web_game_output = GameWebMapper.domain_to_web(domain_game)
        
        # 8. Возвращаем JSON-ответ
        return jsonify(web_game_output.to_dict()), 200

    return app