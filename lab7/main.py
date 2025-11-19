from collections import deque
import heapq

# -----------------------------
# ПАРАМЕТРЫ ЗАДАЧИ (вариант 1)
# -----------------------------
# Большая кружка: 4 литра
# Малая кружка: 3 литра
# Нужно получить 2 литра в ЛЮБОЙ кружке
CAP_X = 4   # вместимость большой кружки
CAP_Y = 3   # вместимость малой кружки
TARGET = 2  # целевое количество воды
START = (0, 0)  # начальное состояние: обе кружки пустые


# -----------------------------
# ПРОСТРАНСТВО СОСТОЯНИЙ
# -----------------------------

def is_goal(s):
    """
    Проверка, является ли состояние s целевым.
    Состояние кодируем как кортеж (x, y),
    где x - вода в большой кружке, y - вода в малой.
    Цель: в любой кружке должно быть ровно TARGET литров.
    """
    x, y = s
    return x == TARGET or y == TARGET


def next_states(state):
    """
    Функция порождает список всех ДОПУСТИМЫХ переходов
    из текущего состояния (x, y).

    Здесь реализованы правила:
    1) наполнить большую
    2) наполнить малую
    3) вылить большую
    4) вылить малую
    5) перелить из большой в малую
    6) перелить из малой в большую
    """
    x, y = state
    res = set()  # set, чтобы не было повторов

    # 1) наполнить большую кружку до 4 л
    if x < CAP_X:
        res.add((CAP_X, y))

    # 2) наполнить малую кружку до 3 л
    if y < CAP_Y:
        res.add((x, CAP_Y))

    # 3) вылить большую кружку
    if x > 0:
        res.add((0, y))

    # 4) вылить малую кружку
    if y > 0:
        res.add((x, 0))

    # 5) перелить из большой в малую
    #    переливаем сколько влезет в малую (до 3 л)
    if x > 0 and y < CAP_Y:
        t = min(x, CAP_Y - y)    # сколько реально перельётся
        res.add((x - t, y + t))

    # 6) перелить из малой в большую
    if y > 0 and x < CAP_X:
        t = min(y, CAP_X - x)
        res.add((x + t, y - t))

    # не считаем переход в самого себя
    res.discard(state)

    # возвращаем список соседних состояний
    return list(res)


def restore_path(parents, end):
    """
    Восстановление пути от START до end по словарю parents.

    parents[child] = parent
    Идём от конечного состояния назад к START,
    собираем цепочку, потом переворачиваем.
    """
    path = []
    s = end
    while s is not None:
        path.append(s)
        s = parents.get(s)
    path.reverse()
    return path


# -----------------------------
# СТРАТЕГИЯ 1: ПОИСК В ШИРИНУ (BFS) — слепой
# -----------------------------

def bfs(start):
    """
    Поиск в ширину (BFS).
    Идея: сначала просматриваем все состояния на расстоянии 1 шага,
    потом 2 шага, и т.д. — поэтому BFS находит КРАТЧАЙШИЙ путь.

    Возвращает:
      path          — найденный путь (список состояний),
      visited_count — сколько состояний было просмотрено.
    """
    # очередь для обхода в ширину
    q = deque([start])

    # словарь родителей: нужен для восстановления пути
    parents = {start: None}

    # множество посещённых состояний (чтобы не зациклиться)
    visited = {start}

    # счётчик просмотренных узлов
    visited_count = 0

    while q:
        # берём состояние из начала очереди
        s = q.popleft()
        visited_count += 1

        # проверяем, не цель ли это
        if is_goal(s):
            path = restore_path(parents, s)
            return path, visited_count

        # перебираем всех соседей
        for ns in next_states(s):
            if ns not in visited:
                visited.add(ns)
                parents[ns] = s
                q.append(ns)

    # если очередь опустела, а цель не найдена
    return None, visited_count


# -----------------------------
# ЭВРИСТИКА И ЖАДНЫЙ ПОИСК
# -----------------------------

def h(s):
    """
    Эвристическая функция h(s).

    Возвращает, насколько мы далеки от цели (2 литра)
    в ЛУЧШЕЙ из кружек.

    Пример:
      s = (4, 1) -> |4-2|=2, |1-2|=1 -> h=1
      s = (2, 0) -> |2-2|=0, |0-2|=2 -> h=0 (идеальное состояние)
    Чем меньше h(s), тем состояние «лучше».
    """
    x, y = s
    return min(abs(TARGET - x), abs(TARGET - y))


def greedy(start):
    """
    Жадный эвристический поиск (Greedy Search).

    Идея:
      - всегда выбираем следующее состояние с ЛУЧШИМ значением h(s),
        не учитывая длину пути (g(s)).
      - это быстрее, чем полный перебор, но решение не всегда
        гарантированно кратчайшее.

    Используем приоритетную очередь (heapq),
    где приоритет = h(s).

    Возвращает:
      path          — найденный путь,
      visited_count — количество просмотренных состояний.
    """
    # куча (min-heap): элементы вида (h(state), state)
    heap = []
    heapq.heappush(heap, (h(start), start))

    parents = {start: None}
    visited = set()
    visited_count = 0

    while heap:
        # достаём состояние с минимальным значением h
        _, s = heapq.heappop(heap)

        # если уже посещали, пропускаем
        if s in visited:
            continue
        visited.add(s)
        visited_count += 1

        # проверяем, не цель ли это
        if is_goal(s):
            path = restore_path(parents, s)
            return path, visited_count

        # добавляем соседей в кучу с приоритетом h(ns)
        for ns in next_states(s):
            if ns not in visited:
                if ns not in parents:
                    parents[ns] = s
                heapq.heappush(heap, (h(ns), ns))

    return None, visited_count


# -----------------------------
# ИССЛЕДОВАТЕЛЬСКАЯ ЧАСТЬ
# -----------------------------

def all_states():
    """
    Все ДОПУСТИМЫЕ состояния пространства:
    x от 0 до 4, y от 0 до 3.
    Всего 5*4 = 20 состояний.
    """
    res = []
    for x in range(CAP_X + 1):
        for y in range(CAP_Y + 1):
            res.append((x, y))
    return res


def prev_states(state):
    """
    Все состояния, из которых за один ход
    можно попасть в 'state'.

    Реализовано простым перебором всех состояний:
    очередное s берём, смотрим next_states(s),
    если среди них есть 'state' — добавляем.
    """
    result = []
    for s in all_states():
        if state in next_states(s):
            result.append(s)
    return result


def backward_bfs():
    """
    ОБРАТНЫЙ ПОИСК (от цели к источнику).

    Идея:
      - берём все целевые состояния (где есть 2 литра),
      - запускаем от них BFS "назад" по prev_states,
      - ищем начальное состояние START.

    Возвращает:
      path          — путь от START до цели,
      visited_count — сколько состояний посмотрели.
    """
    # собираем список всех целевых состояний
    goal_states = [s for s in all_states() if is_goal(s)]

    # очередь BFS
    q = deque(goal_states)

    # parents: для обратного поиска родителем считаем то,
    # из чего мы пришли "назад"
    parents = {g: None for g in goal_states}
    visited = set(goal_states)
    visited_count = 0

    while q:
        s = q.popleft()
        visited_count += 1

        # если дошли до START — восстановим путь
        if s == START:
            path = restore_path(parents, START)
            return path, visited_count

        # двигаемся в предыдущие состояния
        for ps in prev_states(s):
            if ps not in visited:
                visited.add(ps)
                parents[ps] = s
                q.append(ps)

    return None, visited_count


def mixed_search(start):
    """
    СМЕШАННАЯ СТРАТЕГИЯ.

    Шаг 1: делаем ОДИН жадный шаг из start:
           выбираем соседа с лучшей эвристикой h(s).
    Шаг 2: запускаем BFS от полученного состояния.

    Таким образом, в начале используем эвристику,
    а дальше — гарантированно кратчайший поиск в ширину.
    """
    # --- Шаг 1: один greedy-шаг ---
    current = start
    parents = {start: None}
    visited = {start}

    neighbors = next_states(current)
    if neighbors:
        # выбираем соседа с минимальной h
        best = min(neighbors, key=h)
        parents[best] = current
        visited.add(best)
        current = best

    # --- Шаг 2: BFS от current ---
    q = deque([current])
    visited_bfs = set(visited)
    visited_count = len(visited_bfs)

    while q:
        s = q.popleft()
        visited_count += 1

        if is_goal(s):
            path = restore_path(parents, s)
            return path, visited_count

        for ns in next_states(s):
            if ns not in visited_bfs:
                visited_bfs.add(ns)
                if ns not in parents:
                    parents[ns] = s
                q.append(ns)

    return None, visited_count


def build_graph():
    """
    ПОСТРОЕНИЕ ГРАФА ПЕРЕХОДОВ.

    Возвращает словарь:
      ключ   — состояние (x, y),
      значение — список соседних состояний.
    """
    graph = {}
    for s in all_states():
        graph[s] = next_states(s)
    return graph


def print_graph(graph):
    """
    Простая текстовая "визуализация" графа:
    печатаем для каждого состояния список соседей.
    """
    print("Граф переходов (состояние -> соседи):")
    for s, neigh in graph.items():
        print(f"{s} -> {neigh}")


# -----------------------------
# ОСНОВНАЯ ФУНКЦИЯ
# -----------------------------

def main():
    print("Начальное состояние:", START)
    print("Цель: получить 2 литра в любой кружке.\n")

    # --- Стратегия 1: BFS ---
    path_bfs, visited_bfs = bfs(START)
    print("Стратегия 1: поиск в ширину (BFS, слепой)")
    if path_bfs:
        for i, s in enumerate(path_bfs):
            print(f"Шаг {i}: {s}")
        print("Шагов:", len(path_bfs) - 1)
    else:
        print("Решение не найдено.")
    print("Посещено состояний:", visited_bfs, "\n")

    # --- Стратегия 2: Greedy ---
    path_gr, visited_gr = greedy(START)
    print("Стратегия 2: жадный эвристический поиск")
    if path_gr:
        for i, s in enumerate(path_gr):
            print(f"Шаг {i}: {s}")
        print("Шагов:", len(path_gr) - 1)
    else:
        print("Решение не найдено.")
    print("Посещено состояний:", visited_gr, "\n")

    # --- Обратный поиск ---
    path_back, visited_back = backward_bfs()
    print("Обратный поиск (от цели к источнику)")
    if path_back:
        for i, s in enumerate(path_back):
            print(f"Шаг {i}: {s}")
        print("Шагов:", len(path_back) - 1)
    else:
        print("Решение не найдено.")
    print("Посещено состояний:", visited_back, "\n")

    # --- Смешанная стратегия ---
    path_mix, visited_mix = mixed_search(START)
    print("Смешанная стратегия (1 шаг Greedy + BFS)")
    if path_mix:
        for i, s in enumerate(path_mix):
            print(f"Шаг {i}: {s}")
        print("Шагов:", len(path_mix) - 1)
    else:
        print("Решение не найдено.")
    print("Посещено состояний:", visited_mix, "\n")

    # --- Граф переходов ---
    graph = build_graph()
    print_graph(graph)


if __name__ == "__main__":
    main()
