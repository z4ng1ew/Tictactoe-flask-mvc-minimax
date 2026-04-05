#!/bin/bash
# play.sh — клиент для игры в крестики-нолики
# Запуск: ./play.sh [UUID]

BASE_URL="http://127.0.0.1:5000"
GAME_ID="${1:-$(python3 -c 'import uuid; print(uuid.uuid4())')}"

# Цвета (используем printf для надёжности)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # сброс

echo -e "${YELLOW}🎮 Крестики-Нолики${NC}"
echo "Игра ID: $GAME_ID"
echo "Управление: координаты 'строка столбец' (0-2)"
echo "Пример: '0 0' — верхний левый, '1 1' — центр"
echo "Команды: 'quit' — выход, 'board' — показать доску"
echo -e "Легенда: ${GREEN}1 = ты (X)${NC}, ${RED}2 = комп (O)${NC}, 0 = пусто"
echo "=================================================="

CURRENT_MATRIX='[[0,0,0],[0,0,0],[0,0,0]]'

# Функция печати доски
print_board() {
    local matrix="$1"
    echo ""
    echo "    0   1   2"
    echo "  -----------"
    
    # Используем heredoc для правильной интерпретации цветов
    python3 << EOF
import json
m = json.loads('''$matrix''')
for i, row in enumerate(m):
    line = []
    for cell in row:
        if cell == 0:
            line.append(' . ')
        elif cell == 1:
            line.append('$GREEN X $NC')
        else:
            line.append('$RED O $NC')
    print(f'{i} |' + '|'.join(line) + '|')
    print('  -----------')
EOF
    echo ""
}

# Функция отправки хода
make_move() {
    local row=$1
    local col=$2
    
    # Обновляем матрицу: ставим 1 (игрок)
    NEW_MATRIX=$(python3 -c "
import json, sys
try:
    m = json.loads('$CURRENT_MATRIX')
    if m[$row][$col] != 0:
        print('OCCUPIED')
        sys.exit(0)
    m[$row][$col] = 1
    print(json.dumps(m))
except Exception as e:
    print('ERROR:' + str(e))
" 2>/dev/null)
    
    if [[ "$NEW_MATRIX" == "OCCUPIED" ]]; then
        echo -e "${RED}❌ Клетка занята!${NC} Попробуй другую."
        return 1
    elif [[ "$NEW_MATRIX" == ERROR* ]]; then
        echo -e "${RED}❌ Ошибка парсинга: ${NEW_MATRIX#ERROR:}${NC}"
        return 1
    fi
    
    # Отправляем запрос на сервер
    RESPONSE=$(curl -s -X POST "$BASE_URL/game/$GAME_ID" \
      -H "Content-Type: application/json" \
      -d "{
        \"id\": \"$GAME_ID\",
        \"board\": {
          \"matrix\": $NEW_MATRIX,
          \"size\": 3
        }
      }" 2>/dev/null)
    
    # Проверяем ответ
    if ! echo "$RESPONSE" | python3 -c "import sys,json; json.load(sys.stdin)" >/dev/null 2>&1; then
        echo -e "${RED}❌ Ошибка: сервер вернул некорректный ответ${NC}"
        echo "   Ответ: ${RESPONSE:0:100}..."
        return 1
    fi
    
    # Обновляем матрицу из ответа
    CURRENT_MATRIX=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['board']['matrix']))" 2>/dev/null)
    
    if [[ -z "$CURRENT_MATRIX" ]]; then
        echo -e "${RED}❌ Не удалось обновить доску${NC}"
        return 1
    fi
    
    # Показываем обновлённую доску
    print_board "$CURRENT_MATRIX"
    
    # Проверка на окончание игры (нет ли нулей)
    EMPTY=$(echo "$CURRENT_MATRIX" | python3 -c "import sys,json; m=json.load(sys.stdin); print('YES' if any(0 in row for row in m) else 'NO')" 2>/dev/null)
    if [[ "$EMPTY" == "NO" ]]; then
        echo -e "${YELLOW}🏁 Игра окончена! Поле заполнено.${NC}"
        echo "Начни новую: ./play.sh"
        return 2
    fi
    
    return 0
}

# Показываем начальную доску
print_board "$CURRENT_MATRIX"

# Главный цикл
while true; do
    read -p "Твой ход (row col): " input
    
    if [[ "$input" == "quit" || "$input" == "exit" || "$input" == "q" ]]; then
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
        echo -e "${RED}❌ Вводи числа 0-2. Пример: '0 1'${NC}"
        continue
    fi
    
    # Делаем ход
    make_move "$row" "$col"
    result=$?
    
    if [[ $result -eq 2 ]]; then
        break  # Игра окончена
    fi
    # Если результат 1 (ошибка) — просто продолжаем цикл, не выходим
done