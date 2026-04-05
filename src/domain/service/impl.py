from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.model.game import Game
from domain.model.game_board import GameBoard

class GameServiceImpl(GameServiceInterface):
    def get_next_move(self, game: Game) -> Tuple[int, int]:
        """
        Возвращает координаты следующего хода компьютера.
        Если свободных клеток нет — возвращает (-1, -1).
        """
        # Ищем первую свободную клетку (простая стратегия)
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] == 0:
                    return (r, c)
        # Если свободных клеток нет — сигнал "хода нет"
        return (-1, -1)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        """
        Проверяет, что игрок не подменил историю ходов.
        Разница между досками должна быть ровно в 1 клетку.
        """
        if game.board.size != previous_board.size:
            return False
        
        # Считаем, сколько клеток изменилось
        diff_count = 0
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] != previous_board.matrix[r][c]:
                    diff_count += 1
        
        # Валидно только если изменилась ровно 1 клетка (ход игрока)
        return diff_count == 1

    def is_game_over(self, game: Game) -> bool:
        """
        Проверяет окончание игры.
        Игра окончена если:
        1. Доска заполнена (ничья)
        2. Есть победитель (проверка линий)
        """
        # 1. Проверка на заполнение доски (ничья)
        if all(cell != 0 for row in game.board.matrix for cell in row):
            return True
        
        # 2. Проверка на победу (8 возможных линий)
        lines = [
            # Горизонтали
            [(0,0), (0,1), (0,2)], [(1,0), (1,1), (1,2)], [(2,0), (2,1), (2,2)],
            # Вертикали
            [(0,0), (1,0), (2,0)], [(0,1), (1,1), (2,1)], [(0,2), (1,2), (2,2)],
            # Диагонали
            [(0,0), (1,1), (2,2)], [(0,2), (1,1), (2,0)]
        ]
        
        for line in lines:
            cells = [game.board.matrix[r][c] for r, c in line]
            # Если все три клетки не пустые и одинаковые → победа
            if cells[0] != 0 and cells[0] == cells[1] == cells[2]:
                return True
        
        # Игра продолжается
        return False