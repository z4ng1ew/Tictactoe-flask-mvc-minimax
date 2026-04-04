import inspect
import threading

def test_checklist():
    print("🔍 Проверка Задания 3...\n")
    
    # 1. Импорт классов
    from datasource.storage import GameStorage
    from datasource.model.game_ds import GameDS
    from datasource.model.game_board_ds import GameBoardDS
    from datasource.repository.game_repo import GameRepository
    from datasource.mapper.mapper import GameMapper
    from datasource.service.game_service_impl import GameServiceImplWithRepo
    from domain.service.interface import GameServiceInterface
    print("✅ Все классы импортируются из разных файлов.")

    # 2. Потокобезопасность
    storage = GameStorage()
    assert hasattr(storage, '_lock') and isinstance(storage._lock, type(threading.Lock()))
    print("✅ Хранилище использует Lock (потокобезопасность).")

    # 3. Модели datasource
    board_ds = GameBoardDS(matrix=[[0]*3]*3, size=3)
    game_ds = GameDS(id="test-uuid", board=board_ds)
    print("✅ Модели игрового поля и игры в datasource описаны.")

    # 4. Мапперы
    mapper = GameMapper()
    assert hasattr(mapper, 'domain_to_ds') and hasattr(mapper, 'ds_to_domain')
    print("✅ Мапперы domain <-> datasource реализованы.")

    # 5. Репозиторий
    repo = GameRepository(storage)
    assert hasattr(repo, 'save_game') and hasattr(repo, 'get_game')
    repo.save_game(game_ds)
    fetched = repo.get_game("test-uuid")
    assert fetched is not None and fetched.id == "test-uuid"
    print("✅ Репозиторий сохраняет и получает игры.")

    # 6. Сервис с репозиторием
    service = GameServiceImplWithRepo(repo)
    assert isinstance(service, GameServiceInterface)
    assert hasattr(service, 'get_next_move')
    assert hasattr(service, 'validate_board')
    assert hasattr(service, 'is_game_over')
    print("✅ Класс сервиса реализует интерфейс и принимает репозиторий.")
    print("\n🎉 Все пункты чек-листа пройдены успешно!")

if __name__ == "__main__":
    test_checklist()