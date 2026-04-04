from typing import Tuple
from domain.service.interface import GameServiceInterface
from domain.model.game import Game
from domain.model.game_board import GameBoard
from datasource.repository.game_repo import GameRepository
from datasource.mapper.mapper import GameMapper

class GameServiceImplWithRepo(GameServiceInterface):
    def __init__(self, repository: GameRepository):
        self._repo = repository
        self._mapper = GameMapper()

    def get_next_move(self, game: Game) -> Tuple[int, int]:
        # Заглушка под Минимакс. В реальном проекте здесь рекурсия.
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.matrix[r][c] == 0:
                    return (r, c)
        return (0, 0)

    def validate_board(self, game: Game, previous_board: GameBoard) -> bool:
        diff = sum(1 for r in range(game.board.size) 
                   for c in range(game.board.size) 
                   if game.board.matrix[r][c] != previous_board.matrix[r][c])
        return diff == 1

    def is_game_over(self, game: Game) -> bool:
        return all(cell != 0 for row in game.board.matrix for cell in row)

    def save_game_state(self, game: Game) -> None:
        """Сохраняет текущее состояние игры в репозиторий."""
        # Переводим domain-модель в datasource-модель через маппер
        game_ds = self._mapper.domain_to_ds(game)
        self._repo.save_game(game_ds)

    def get_previous_board(self, game_id: str) -> GameBoard | None:
        """
        Загружает предыдущее состояние доски из репозитория.
        Возвращает None, если игра ещё не начиналась (первый ход).
        """
        game_ds = self._repo.get_game(game_id)
        if game_ds is None:
            return None
        # Переводим datasource-модель обратно в domain-модель
        return self._mapper.ds_to_domain(game_ds).board