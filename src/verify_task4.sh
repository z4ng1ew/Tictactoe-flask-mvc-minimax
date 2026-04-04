#!/bin/bash
# verify_task4.sh — автоматическая проверка Задания 4
# Запуск: bash verify_task4.sh (находясь в src/)

echo "🔍 Проверка Задания 4 (web-слой) по чек-листу..."
echo "================================================"

PASS=0
TOTAL=6

# 1. Модели игрового поля и игры в web
echo -n "1. Модели web (GameWeb, GameBoardWeb)... "
if grep -q "@dataclass" web/model/game_web.py && \
   grep -q "class GameWeb" web/model/game_web.py && \
   grep -q "class GameBoardWeb" web/model/game_board_web.py; then
    echo "✅"
    ((PASS++))
else
    echo "❌ Не найдены @dataclass или классы"
fi

# 2. Мапперы domain <-> web
echo -n "2. Мапперы domain <-> web... "
if grep -q "domain_to_web" web/mapper/mapper.py && \
   grep -q "web_to_domain" web/mapper/mapper.py && \
   grep -q "GameWebMapper" web/mapper/mapper.py; then
    echo "✅"
    ((PASS++))
else
    echo "❌ Не найдены методы маппера"
fi

# 3. Контроллер Flask с POST /game/<UUID>
echo -n "3. Flask-контроллер с POST /game/<UUID>... "
if grep -q "@app.route.*/game/.*<string:game_id>.*methods.*POST" web/route/controller.py && \
   grep -q "from flask import" web/route/controller.py && \
   grep -q "def handle_game_move" web/route/controller.py; then
    echo "✅"
    ((PASS++))
else
    echo "❌ Не найден маршрут или импорт Flask"
fi

# 4. Обработка ошибок (400 с описанием)
echo -n "4. Возврат ошибки 400 с описанием... "
if grep -q "abort(400" web/route/controller.py && \
   grep -q "description=" web/route/controller.py; then
    echo "✅"
    ((PASS++))
else
    echo "❌ Не найдена обработка ошибок через abort(400)"
fi

# 5. Поддержка нескольких игр (хранилище не глобальное)
echo -n "5. Поддержка нескольких игр (изолированное хранилище)... "
if grep -q "class GameStorage" datasource/storage.py && \
   grep -q "self._store: Dict" datasource/storage.py && \
   ! grep -q "GLOBAL_STORAGE\s*=" datasource/storage.py; then
    echo "✅"
    ((PASS++))
else
    echo "❌ Хранилище может быть глобальным или не найдено"
fi

# 6. Разделение на разные файлы
echo -n "6. Модели/мапперы/контроллер в разных файлах... "
FILES_OK=true
for f in web/model/game_web.py web/model/game_board_web.py web/mapper/mapper.py web/route/controller.py; do
    if [ ! -f "$f" ]; then
        echo "❌ Отсутствует файл: $f"
        FILES_OK=false
        break
    fi
done
if $FILES_OK; then
    echo "✅"
    ((PASS++))
else
    echo ""
fi

# Итог
echo "================================================"
if [ $PASS -eq $TOTAL ]; then
    echo "🎉 Все $TOTAL пунктов чек-листа пройдены!"
    echo "✅ Задание 4 выполнено полностью."
    exit 0
else
    echo "⚠️  Пройдено: $PASS из $TOTAL пунктов"
    echo "❌ Проверь отмеченные пункты выше"
    exit 1
fi