#!/bin/bash
# play.sh — простой клиент для игры в крестики-нолики
# Запуск: ./play.sh [UUID]
# Если UUID не указан — создастся новый

set -e

BASE_URL="http://127.0.0.1:5000"
GAME_ID="${1:-$(python3 -c 'import uuid; print(uuid.uuid4())')}"

# Цвета для красоты
RED='\033[0;31m'    # компьютер (2)
GREEN='\033[0;32m'  # игрок (1)
NC='\033[0m'        # сброс цвета
YELLOW='\033[1;33m'

echo -e "${YELLOW}🎮 Крестики-Нолики${NC}"
echo "Игра ID: $GAME_ID"
echo "Управление: вводи координаты как 'строка столбец' (0-2)"
echo "Пример: '0 0' — верхний левый угол, '1 1' — центр"
echo "Команды: 'quit' — выход, 'board' — показать текущую доску"
echo "Легенда: ${GREEN}1 = ты${NC}, ${RED}2 = компьютер${NC}, 0 = пусто"
echo "=================================================="

# Пустая доска для начала
CURRENT_MATRIX='[[0,0,0],[0,0,0],[0,0,0]]'

# Функция для красивой печати доски
print_board() {
    local matrix="$1"
    echo ""
    echo "  0   1   2"
    echo "  -----------"
    python3 -c "
import json
m = json.loads('$matrix')
for i, row in enumerate(m):
    line = []
    for cell in row:
        if cell == 0:
            line.append(' . ')
        elif cell == 1:
            line.append('${GREEN} X ${NC}')
        else:
            line.append('${RED} O ${NC}')
    print(f'{i} |' + '|'.join(line) + '|')
    print('  -----------')
"
    echo ""
}

# Функция отправки хода
make_move() {
    local row=$1
    local col=$2
    
    # Обновляем матрицу: ставим 1 (игрок) в указанную клетку
    NEW_MATRIX=$(python3 -c "
import json
m = json.loads('$CURRENT_MATRIX')
if m[$row][$col] == 0:
    m[$row][$col] = 1
    print(json.dumps(m))
else:
    print('ERROR')
")
    
    if [[ "$NEW_MATRIX" == "ERROR" ]]; then
        echo "❌ Клетка уже занята! Попробуй другую."
        return 1
    fi
    
    # Отправляем запрос
    RESPONSE=$(curl -s -X POST "$BASE_URL/game/$GAME_ID" \
      -H "Content-Type: application/json" \
      -d "{
        \"id\": \"$GAME_ID\",
        \"board\": {
          \"matrix\": $NEW_MATRIX,
          \"size\": 3
        }
      }")
    
    # Парсим ответ
    STATUS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if 'board' in d else 'ERR')")
    
    if [[ "$STATUS" == "OK" ]]; then
        # Обновляем текущую матрицу и печатаем
        CURRENT_MATRIX=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['board']['matrix']))")
        print_board "$CURRENT_MATRIX"
        
        # Проверяем окончание игры (упрощённо: если нет нулей)
        EMPTY=$(echo "$CURRENT_MATRIX" | python3 -c "import sys,json; m=json.load(sys.stdin); print('YES' if any(0 in row for row in m) else 'NO')")
        if [[ "$EMPTY" == "NO" ]]; then
            echo "🏁 Игра окончена! Поле заполнено."
            echo "Начни новую: ./play.sh"
            return 2
        fi
        return 0
    else
        echo "❌ Ошибка сервера: $RESPONSE"
        return 1
    fi
}

# Главный цикл игры
print_board "$CURRENT_MATRIX"

while true; do
    read -p "Твой ход (row col): " input
    
    if [[ "$input" == "quit" ]]; then
        echo "👋 Пока!"
        break
    elif [[ "$input" == "board" ]]; then
        print_board "$CURRENT_MATRIX"
        continue
    fi
    
    # Парсим ввод
    read row col <<< "$input"
    
    # Валидация
    if ! [[ "$row" =~ ^[0-2]$ && "$col" =~ ^[0-2]$ ]]; then
        echo "❌ Вводи числа от 0 до 2. Пример: '0 1'"
        continue
    fi
    
    # Делаем ход
    make_move "$row" "$col"
    result=$?
    
    if [[ $result -eq 2 ]]; then
        break  # Игра окончена
    fi
done