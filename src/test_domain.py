from domain import Game, GameBoard, GameServiceImpl

game = Game()
prev = game.board.copy()
service = GameServiceImpl()

print("Валидация до хода:", service.validate_board(game, prev)) # True? False (0 изменений)
game.board.matrix[0][0] = 1
print("Валидация после хода:", service.validate_board(game, prev)) # True (1 изменение)
print("Игра окончена?", service.is_game_over(game)) # False
print("Следующий ход:", service.get_next_move(game))