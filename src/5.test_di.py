def test_di_checklist():
    print("🔍 Проверка Задания 5 (DI-слой)...\n")
    
    # 1. Импорт контейнера
    from di import Container
    print("✅ Класс Container описан в слое di.")
    
    # 2. Singleton для хранилища
    container = Container()
    storage1 = container.get("storage")
    storage2 = container.get("storage")
    assert storage1 is storage2, "Storage должен быть singleton"
    print("✅ GameStorage зарегистрирован как singleton (один экземпляр на приложение).")
    
    # 3. Граф зависимостей
    repo = container.get("repository")
    service = container.get("service")
    app = container.get("controller")
    
    from flask import Flask
    from datasource.repository.game_repo import GameRepository
    from datasource.service.game_service_impl import GameServiceImplWithRepo
    
    assert isinstance(repo, GameRepository)
    assert isinstance(service, GameServiceImplWithRepo)
    assert isinstance(app, Flask)
    print("✅ Граф зависимостей работает: Storage → Repository → Service → Controller.")
    
    # 4. main.py использует контейнер
    import os
    with open("main.py", "r", encoding="utf-8") as f:
        main_code = f.read()
    assert "Container()" in main_code
    assert "container.get(" in main_code
    print("✅ main.py использует контейнер для сборки приложения (нет ручного new).")
    
    # 5. Разделение на файлы
    assert os.path.exists("di/container.py")
    assert os.path.exists("di/__init__.py")
    print("✅ Реализация DI находится в отдельных файлах слоя di.")
    
    print("\n🎉 Все пункты чек-листа Задания 5 пройдены!")
    print("✨ Проект полностью собран и готов к сдаче!")

if __name__ == "__main__":
    test_di_checklist()