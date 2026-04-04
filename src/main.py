# main.py — Точка входа в приложение
from di import Container

if __name__ == "__main__":
    # 1. Создаём контейнер — он сам соберёт все зависимости
    container = Container()
    
    # 2. Получаем готовый Flask-приложение из контейнера
    app = container.get("controller")
    
    # 3. Запускаем сервер
    app.run(host='0.0.0.0', port=5000, debug=True)