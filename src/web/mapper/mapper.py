# Импортируем uuid для работы с уникальными идентификаторами
import uuid
# Импортируем классы из domain-слоя (бизнес-логика)
from domain.model.game import Game
from domain.model.game_board import GameBoard
# Импортируем классы из web-слоя (HTTP-представление)
from web.model.game_web import GameWeb
from web.model.game_board_web import GameBoardWeb

# Класс-маппер: переводчик между слоями
class GameWebMapper:
    # @staticmethod — декоратор: метод не использует self, можно вызывать от класса
    @staticmethod
    def domain_to_web(domain_game: Game) -> GameWeb:
        """
        Переводит объект Game (domain) в GameWeb (web).
        :param domain_game: объект бизнес-модели
        :return: объект для отправки в JSON
        """
        # .matrix — обращаемся к полю объекта
        # .copy() — создаём копию списка, чтобы не менять оригинал
        board_web = GameBoardWeb(
            matrix=domain_game.board.matrix.copy(),
            size=domain_game.board.size
        )
        # str(...) — преобразует объект UUID в строку
        return GameWeb(id=str(domain_game.id), board=board_web)

    @staticmethod
    def web_to_domain(web_game: GameWeb) -> Game:
        """
        Переводит объект GameWeb (web) в Game (domain).
        :param web_game: объект из HTTP-запроса
        :return: объект бизнес-логики
        """
        board_domain = GameBoard(
            matrix=web_game.board.matrix.copy(),
            size=web_game.board.size
        )
        # Создаём объект Game с готовой доской
        game = Game(board=board_domain)
        # uuid.UUID(...) — преобразует строку обратно в объект UUID
        game.id = uuid.UUID(web_game.id)
        return game