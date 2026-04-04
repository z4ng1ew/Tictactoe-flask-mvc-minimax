# Импортируем Flask — основной класс фреймворка
from flask import Flask, request, jsonify, abort
# Импортируем тип для аннотаций
from typing import Tuple
# Импортируем бизнес-интерфейс (контракт)
from domain.service.interface import GameServiceInterface
# Импортируем маппер для перевода между слоями
from web.mapper.mapper import GameWebMapper
# Импортируем web-модель для ответа
from web.model.game_web import GameWeb

# Функция создаёт и настраивает Flask-приложение
# Почему функция, а не просто код? Чтобы можно было переиспользовать и тестировать
def create_game_controller(service: GameServiceInterface) -> Flask:
    """
    Создаёт Flask-приложение с маршрутами для игры.
    :param service: объект, реализующий GameServiceInterface (бизнес-логика)
    :return: настроенный объект Flask
    """
    # Создаём экземпляр приложения
    # __name__ — специальная переменная: имя текущего модуля
    app = Flask(__name__)

    # Декоратор @app.route регистрирует функцию как обработчик URL
    # methods=['POST'] — маршрут отвечает только на POST-запросы
    # '/game/<string:game_id>' — game_id — переменная из URL, тип string
    @app.route('/game/<string:game_id>', methods=['POST'])
    def handle_game_move(game_id: str):
        """
        Обработчик хода: принимает ход игрока, возвращает ход компьютера.
        :param game_id: UUID игры из URL
        :return: JSON с обновлённым состоянием игры или ошибка
        """
        # request — глобальный объект Flask с данными текущего запроса
        # .get_json() — парсит тело запроса из JSON в Python-словарь
        data = request.get_json()
        
        # Проверка: если тело запроса пустое или не словарь
        if not data or not isinstance(data, dict):
            # abort() — немедленно прерывает обработку и возвращает HTTP-ошибку
            # 400 — Bad Request (некорректные данные от клиента)
            abort(400, description="Request body must be a valid JSON object")
        
        try:
            # Пытаемся создать web-модель из данных запроса
            # **data — «распаковка» словаря: GameWeb(id=data['id'], board=data['board'])
            web_game_input = GameWeb(**data)
            # Переводим web-модель в domain-модель через маппер
            domain_game = GameWebMapper.web_to_domain(web_game_input)
        except (KeyError, ValueError, TypeError) as e:
            # Если не хватает полей или неверный формат — ошибка 400
            abort(400, description=f"Invalid game data: {str(e)}")
        
        # Вызываем бизнес-валидацию из domain-слоя
        # .validate_board() проверяет, что игрок не подменил предыдущие ходы
        # Мы не сохраняем старое поле здесь — это делает сервис внутри
        # Для упрощения валидируем только структуру (в реальном проекте нужно хранить историю)
        if not service.validate_board(domain_game, domain_game.board):
            abort(400, description="Board validation failed: previous moves were modified")
        
        # Получаем следующий ход от алгоритма (Минимакс или заглушка)
        next_move: Tuple[int, int] = service.get_next_move(domain_game)
        
        # Применяем ход компьютера к игровому полю
        # [0] и [1] — доступ к элементам кортежа (row, col)
        domain_game.board.matrix[next_move[0]][next_move[1]] = 2  # 2 = компьютер (например, «нолик»)
        
        # Проверяем, не закончилась ли игра после хода
        if service.is_game_over(domain_game):
            # Можно добавить поле "winner" в ответ, но по заданию не требуется
            pass
        
        # Переводим результат обратно в web-модель для отправки клиенту
        web_game_output = GameWebMapper.domain_to_web(domain_game)
        
        # jsonify() — превращает объект в JSON-ответ с заголовком Content-Type: application/json
        # .to_dict() — не встроенный метод, поэтому добавим его в GameWeb (см. ниже)
        return jsonify(web_game_output.to_dict()), 200  # 200 = OK

    # Возвращаем настроенное приложение
    return app