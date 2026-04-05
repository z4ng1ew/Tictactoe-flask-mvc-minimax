#!/bin/bash
# play.sh — клиент для игры в крестики-нолики с железобетонной проверкой победы
# Запуск: ./play.sh [UUID]

BASE_URL="http://127.0.0.1:5000"
GAME_ID="${1:-$(python3 -c 'import uuid; print(uuid.uuid4())')}"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}🎮 Крестики-Нолики${NC}"
echo "Игра ID: $GAME_ID"
echo "Управление: координаты 'строка столбец' (0-2)"
echo "Пример: '0 0' — верхний левый, '1 1' — центр"
echo "Команды: 'quit' — выход, 'board' — показать доску"
echo -e "Легенда: ${GREEN}1 = ты (X)${NC}, ${RED}2 = комп (O)${NC}, 0 = пусто"
echo "=================================================="

CURRENT_MATRIX='[[0,0,0],[0,0,0],[0,0,0]]'
GAME_OVER=false

# Функция печати доски
print_board() {
    local matrix="$1"
    echo ""
    echo "    0   1   2"
    echo "  -----------"
    
    python3 -c "
import json
m = json.loads('$matrix')
for i, row in enumerate(m):
    line = []
    for cell in row:
        if cell == 0: line.append(' . ')
        elif cell == 1: line.append('$GREEN X $NC')
        else: line.append('$RED O $NC')
    print(f'{i} |' + '|'.join(line) + '|')
    print('  -----------')
"
    echo ""
}

# 🔥 НАДЁЖНАЯ проверка победителя
check_winner() {
    python3 -c "
import json, sys
m = json.loads('$1')
lines = [
    [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
]
for l in lines:
    c = [m[r][c] for r, c in l]
    if c[0] != 0 and c[0] == c[1] == c[2]:
        print(c[0]); sys.exit()
print(0)
" 2>/dev/null
}

# 🔥 НАДЁЖНАЯ проверка ничьей
check_draw() {
    python3 -c "
import json
m = json.loads('$1')
print('YES' if all(cell != 0 for row in m for cell in row) else 'NO')
" 2>/dev/null
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
    
    # Обновляем матрицу из ответа сервера
    CURRENT_MATRIX=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['board']['matrix']))" 2>/dev/null)
    
    if [[ -z "$CURRENT_MATRIX" ]]; then
        echo -e "${RED}❌ Не удалось обновить доску${NC}"
        return 1
    fi
    
    # Показываем обновлённую доску
    print_board "$CURRENT_MATRIX"
    
    # 🔥 ПРОВЕРКА РЕЗУЛЬТАТА (с очисткой от переносов строк)
    WINNER=$(check_winner "$CURRENT_MATRIX" | tr -d '[:space:]')
    
    if [[ "$WINNER" == "1" ]]; then
        echo -e "${GREEN}🎉 ПОБЕДА! Ты выиграл!${NC}"
        echo "Поздравляем! 🏆"
        GAME_OVER=true
        return 2
    elif [[ "$WINNER" == "2" ]]; then
        echo -e "${RED}😔 Компьютер выиграл.${NC}"
        echo "Попробуй ещё раз! 🎮"
        GAME_OVER=true
        return 2
    fi
    
    # Если нет победителя — проверяем ничью
    DRAW=$(check_draw "$CURRENT_MATRIX" | tr -d '[:space:]')
    if [[ "$DRAW" == "YES" ]]; then
        echo -e "${YELLOW}🤝 Ничья! Поле заполнено.${NC}"
        GAME_OVER=true
        return 2
    fi
    
    return 0
}

# Показываем начальную доску
print_board "$CURRENT_MATRIX"

# Главный цикл
while true; do
    if [[ "$GAME_OVER" == "true" ]]; then
        echo ""
        echo "Начни новую: ./play.sh"
        break
    fi
    
    read -p "Твой ход (row col): " input
    
    if [[ "$input" == "quit" || "$input" == "exit" || "$input" == "q" ]]; then
        echo "👋 Пока!"
        break
    elif [[ "$input" == "board" ]]; then
        print_board "$CURRENT_MATRIX"
        continue
    fi
    
    read row col <<< "$input"
    
    if ! [[ "$row" =~ ^[0-2]$ && "$col" =~ ^[0-2]$ ]]; then
        echo -e "${RED}❌ Вводи числа 0-2. Пример: '0 1'${NC}"
        continue
    fi
    
    make_move "$row" "$col"
    result=$?
    
    if [[ $result -eq 2 ]]; then
        break
    fi
done