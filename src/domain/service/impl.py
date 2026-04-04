from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.model.game import Game
from domain.model.game_board import GameBoard

class GameServiceImpl(GameServiceInterface):
    def get_next_move(self, game: Game) -> Tuple[int, int]:
        # TODO: Здесь разворачивается полноценный рекурсивный Minimax
        # Для архитектуры достаточно показать контракт и точку входа.
        # Пока возвращаем первую свободную клетку.
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] == 0:
                    return (r, c)
        return (0, 0)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        if game.board.size != previous_board.size:
            return False
        
        # Считаем, сколько клеток изменилось.
        # В пошаговой игре за один ход должна измениться ровно 1 клетка.
        diff_count = 0
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] != previous_board.matrix[r][c]:
                    diff_count += 1
        return diff_count == 1

    def is_game_over(self, game: Game) -> bool:
        # Упрощённая проверка: если на поле нет нулей → доска заполнена
        # В реальном проекте тут будет проверка строк/столбцов/диагоналей
        for row in game.board.matrix:
            if 0 in row:
                return False
        return True