from collections import deque
import time
import heapq

# ОПИСАНИЕ СРЕДЫ (МИНИМАЛЬНОЕ)

# Поле 2×2:
# (0,0) (1,0)
# (0,1) (1,1)
#
# Робот начинает в клетке (0,0).
# Предмет лежит в клетке (1,1).
# Цель: робот должен взять предмет и вернуться обратно в (0,0).
#
# Состояние описывается кортежем:
#   (x, y, has_item)
# где:
#   x, y — координаты робота,
#   has_item — флаг, взял ли робот предмет (True/False)

WIDTH = 2
HEIGHT = 2

BASE = (0, 0)           # начальная позиция
ITEM_POS = (1, 1)       # место, где лежит предмет


def make_state(x, y, has_item):
    """Создаёт состояние (клетка + взят ли предмет)."""
    return (x, y, has_item)


# Начальное состояние: робот в (0,0), предмет ещё не взял
START_STATE = make_state(BASE[0], BASE[1], False)

# Целевое состояние: робот в (0,0), предмет взят
GOAL_STATE = make_state(BASE[0], BASE[1], True)


def is_inside(x, y):
    """Проверяет, находится ли клетка внутри поля."""
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def is_goal(state):
    """Проверяет, является ли состояние целевым."""
    return state == GOAL_STATE


# ПРЕОБРАЗОВАНИЯ СОСТОЯНИЙ (ПРЯМЫЕ ПЕРЕХОДЫ)

def successors_forward(state):
    """
    Возвращает список возможных следующих состояний (ОБЫЧНЫЙ поиск).
    Доступные действия:
      1) перемещение вверх/вниз/влево/вправо (если не выходим за поле)
      2) взять предмет, если робот стоит на позиции предмета
    """
    x, y, has_item = state
    result = []

    # Все возможные перемещения (смещения по координатам)
    moves = [
        ("up", (0, -1)),
        ("down", (0, 1)),
        ("left", (-1, 0)),
        ("right", (1, 0)),
    ]

    # Пробуем каждый из четырёх шагов
    for name, (dx, dy) in moves:
        nx, ny = x + dx, y + dy
        if is_inside(nx, ny):
            # Двигаемся в новую клетку, флаг предмета не меняется
            result.append((make_state(nx, ny, has_item), f"move_{name}"))

    # Проверка: если робот в клетке предмета и предмет ещё не взял — можно взять
    if (x, y) == ITEM_POS and not has_item:
        result.append((make_state(x, y, True), "pickup"))

    return result


# ОБРАТНЫЕ ПЕРЕХОДЫ (используются в обратном поиске)

def predecessors_backward(state):
    """
    Возвращает возможные предыдущие состояния (ОБРАТНЫЙ поиск).
    Логика:
      - в прошлый момент робот мог стоять на соседней клетке и перейти сюда
      - если робот сейчас держит предмет и стоит на его клетке, раньше мог его НЕ держать
    """
    x, y, has_item = state
    result = []

    # Шаги "в обратную сторону":
    # если робот сейчас в (x,y), раньше он мог быть в (x-dx, y-dy)
    moves = [
        ("up", (0, -1)),
        ("down", (0, 1)),
        ("left", (-1, 0)),
        ("right", (1, 0)),
    ]

    for name, (dx, dy) in moves:
        px, py = x - dx, y - dy  # обратное движение
        if is_inside(px, py):
            result.append((make_state(px, py, has_item), f"move_{name}_back"))

    # Если у робота сейчас предмет и он стоит на позиции предмета,
    # то раньше он мог стоять здесь же, но предмет не брать.
    if (x, y) == ITEM_POS and has_item:
        result.append((make_state(x, y, False), "unpickup"))

    return result


# ЭВРИСТИКА

def heuristic(state):
    """
    Простая эвристика:
    - если предмет не взят: расстояние до предмета + расстояние от предмета до базы
    - если предмет уже взят: расстояние до базы
    Это НЕ идеальная эвристика, но допустимая и даёт выигрыш.
    """
    x, y, has_item = state

    # Манхэттеновские расстояния
    dist_to_base = abs(x - BASE[0]) + abs(y - BASE[1])
    dist_to_item = abs(x - ITEM_POS[0]) + abs(y - ITEM_POS[1])
    item_to_base = abs(ITEM_POS[0] - BASE[0]) + abs(ITEM_POS[1] - BASE[1])

    if not has_item:
        # сначала нужно дойти до предмета, потом вернуться к базе
        return dist_to_item + item_to_base
    else:
        # предмет уже взят — просто идти домой
        return dist_to_base


# Восстановление пути из словаря родителей

def reconstruct_path(parents, end_state):
    """
    Двигаемся назад: конечное состояние -> родитель -> родитель -> ...
    После чего переворачиваем путь.
    """
    path = []
    s = end_state
    while s is not None:
        path.append(s)
        s = parents.get(s)
    path.reverse()
    return path


# ПРЯМОЙ BFS

def bfs_forward():
    """
    Простой поиск в ширину (без эвристики).
    Гарантирует нахождение кратчайшего пути.
    """
    start_time = time.perf_counter()

    queue = deque([START_STATE])     # очередь на исследование
    parents = {START_STATE: None}    # храним родителей для восстановления пути
    visited_count = 0
    generated_count = 0
    found_state = None

    # Пока есть состояния для исследования
    while queue:
        state = queue.popleft()
        visited_count += 1

        # Проверка цели
        if is_goal(state):
            found_state = state
            break

        # Генерация следующих состояний
        for new_state, _ in successors_forward(state):
            generated_count += 1
            if new_state not in parents:
                parents[new_state] = state
                queue.append(new_state)

    elapsed = time.perf_counter() - start_time

    if found_state is None:
        return None, visited_count, generated_count, 0.0, elapsed

    # восстановление пути
    path = reconstruct_path(parents, found_state)

    # коэффициент разветвления (формула из задания)
    b = generated_count / visited_count if visited_count else 0.0
    return path, visited_count, generated_count, b, elapsed


# ПРЯМОЙ ЖАДНЫЙ ПОИСК С ЭВРИСТИКОЙ

def greedy_forward():
    """
    Жадный поиск по наилучшей эвристике:
    - выбираем состояние с минимальным h()
    Не гарантирует кратчайший путь в общем случае,
    но у нас задача маленькая, и результат оптимален.
    """
    start_time = time.perf_counter()
    heap = []                       # приоритетная очередь
    counter = 0

    # кладём старт по приоритету = h(старт)
    heapq.heappush(heap, (heuristic(START_STATE), counter, START_STATE))

    parents = {START_STATE: None}
    in_open = {START_STATE}
    visited_count = 0
    generated_count = 0
    found_state = None

    while heap:
        h, _, state = heapq.heappop(heap)

        # проверяем, что состояние ещё актуальное
        if state not in in_open:
            continue
        in_open.remove(state)

        visited_count += 1

        if is_goal(state):
            found_state = state
            break

        # генерируем потомков
        for new_state, _ in successors_forward(state):
            generated_count += 1
            if new_state not in parents:
                parents[new_state] = state
                counter += 1
                heapq.heappush(heap, (heuristic(new_state), counter, new_state))
                in_open.add(new_state)

    elapsed = time.perf_counter() - start_time

    if found_state is None:
        return None, visited_count, generated_count, 0.0, elapsed

    path = reconstruct_path(parents, found_state)
    b = generated_count / visited_count if visited_count else 0.0
    return path, visited_count, generated_count, b, elapsed


# ОБРАТНЫЙ ЖАДНЫЙ ПОИСК

def greedy_backward():
    """
    Обратный жадный поиск:
    - стартуем от цели и идём назад по эвристике
    - когда добираемся до START_STATE — путь найден
    """
    start_time = time.perf_counter()
    heap = []
    counter = 0

    heapq.heappush(heap, (heuristic(GOAL_STATE), counter, GOAL_STATE))

    parents = {GOAL_STATE: None}
    in_open = {GOAL_STATE}
    visited_count = 0
    generated_count = 0
    found_state = None

    while heap:
        h, _, state = heapq.heappop(heap)
        if state not in in_open:
            continue
        in_open.remove(state)

        visited_count += 1

        # цель обратного поиска — прийти в начальное состояние
        if state == START_STATE:
            found_state = state
            break

        # генерируем возможных предшественников
        for prev_state, _ in predecessors_backward(state):
            generated_count += 1
            if prev_state not in parents:
                parents[prev_state] = state
                counter += 1
                heapq.heappush(heap, (heuristic(prev_state), counter, prev_state))
                in_open.add(prev_state)

    elapsed = time.perf_counter() - start_time

    if found_state is None:
        return None, visited_count, generated_count, 0.0, elapsed

    # Восстанавливаем путь от старта
    path = reconstruct_path(parents, START_STATE)
    b = generated_count / visited_count if visited_count else 0.0
    return path, visited_count, generated_count, b, elapsed


# ДВУНАПРАВЛЕННЫЙ BFS

def bidirectional_bfs():
    """
    Двунаправленный BFS:
    - одновременно двигаемся от старта и от цели
    - когда фронты встречаются — путь найден
    """
    start_time = time.perf_counter()

    # если старт уже равен цели
    if START_STATE == GOAL_STATE:
        return [START_STATE], 0, 0, 0.0, 0.0

    # Очереди поиска
    q_start = deque([START_STATE])
    q_goal = deque([GOAL_STATE])

    # Родители для восстановления пути
    parents_start = {START_STATE: None}
    parents_goal = {GOAL_STATE: None}

    # Множества посещённых состояний
    visited_from_start = {START_STATE}
    visited_from_goal = {GOAL_STATE}

    visited_count = 0
    generated_count = 0
    meeting_state = None  # где встретились два поиска

    while q_start and q_goal and meeting_state is None:

        # ==== 1. Шаг из старта ====
        for _ in range(len(q_start)):
            state = q_start.popleft()
            visited_count += 1

            for new_state, _ in successors_forward(state):
                generated_count += 1
                if new_state not in visited_from_start:
                    visited_from_start.add(new_state)
                    parents_start[new_state] = state
                    q_start.append(new_state)

                    # если состояние уже посещено обратным поиском
                    if new_state in visited_from_goal:
                        meeting_state = new_state
                        break
            if meeting_state:
                break

        if meeting_state:
            break

        # ==== 2. Шаг из конца ====
        for _ in range(len(q_goal)):
            state = q_goal.popleft()
            visited_count += 1

            for prev_state, _ in predecessors_backward(state):
                generated_count += 1
                if prev_state not in visited_from_goal:
                    visited_from_goal.add(prev_state)
                    parents_goal[prev_state] = state
                    q_goal.append(prev_state)

                    # встреча с прямым поиском
                    if prev_state in visited_from_start:
                        meeting_state = prev_state
                        break
            if meeting_state:
                break

    elapsed = time.perf_counter() - start_time

    if meeting_state is None:
        return None, visited_count, generated_count, 0.0, elapsed

    # Восстанавливаем путь от старта до точки встречи
    path1 = []
    s = meeting_state
    while s is not None:
        path1.append(s)
        s = parents_start.get(s)
    path1.reverse()

    # Восстанавливаем путь от точки встречи до цели
    path2 = []
    s = parents_goal.get(meeting_state)
    while s is not None:
        path2.append(s)
        s = parents_goal.get(s)

    full_path = path1 + path2

    b = generated_count / visited_count if visited_count else 0.0
    return full_path, visited_count, generated_count, b, elapsed


# ЗАПУСК ВСЕХ АЛГОРИТМОВ

def run_all():
    print("Стартовое состояние:", START_STATE)
    print("Целевое состояние:", GOAL_STATE)
    print()

    print("Прямой поиск (BFS)")
    path, visited, generated, b, t = bfs_forward()
    print("Путь:", path)
    print("Длина решения:", len(path) - 1 if path else None)
    print("Посещённых вершин:", visited)
    print("Сгенерировано состояний:", generated)
    print("Коэффициент разветвления:", round(b, 2))
    print("Время:", f"{t:.6f} c")
    print()

    print("Прямой жадный поиск с эвристикой")
    path, visited, generated, b, t = greedy_forward()
    print("Путь:", path)
    print("Длина решения:", len(path) - 1 if path else None)
    print("Посещённых вершин:", visited)
    print("Сгенрировано состояний:", generated)
    print("Коэффициент разветвления:", round(b, 2))
    print("Время:", f"{t:.6f} c")
    print()

    print("Обратный жадный поиск с эвристикой")
    path, visited, generated, b, t = greedy_backward()
    print("Путь:", path)
    print("Длина решения:", len(path) - 1 if path else None)
    print("Посещённых вершин:", visited)
    print("Сгенерировано состояний:", generated)
    print("Коэффициент разветвления:", round(b, 2))
    print("Время:", f"{t:.6f} c")
    print()

    print("Двунаправленный поиск (BFS)")
    path, visited, generated, b, t = bidirectional_bfs()
    print("Путь:", path)
    print("Длина решения:", len(path) - 1 if path else None)
    print("Посещённых вершин:", visited)
    print("Сгенерировано состояний:", generated)
    print("Коэффициент разветвления:", round(b, 2))
    print("Время:", f"{t:.6f} c")


if __name__ == "__main__":
    run_all()
