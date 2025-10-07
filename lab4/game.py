# Логика поля: генерация, вставка паттерна, шаг правил, отрисовка

from typing import List, Tuple
import random

ALIVE = "█"   # Символ живой клетки 
DEAD  = " "   # Мёртвая клетка

Grid = List[List[int]]

class Game:
    def __init__(self, h: int, w: int):
        self.H, self.W = h, w
        self.g: Grid = [[0]*w for _ in range(h)]  # Пустое поле

    def random_init(self, p_alive: float, rng: random.Random) -> None:
        """Случайное заполнение: живая с вероятностью p_alive."""
        for i in range(self.H):
            for j in range(self.W):
                self.g[i][j] = 1 if rng.random() < p_alive else 0

    def place_pattern_safely(self, pattern: Grid, rng: random.Random, max_tries: int = 200) -> Tuple[int,int,bool]:
        """
        Ставим паттерн в «почти пустое» окно (<=1 живой).
        Если не нашли быстро — ставим в случайное место.
        Возврат: (x, y, найдено_пустое_окно)
        """
        h, w = len(pattern), len(pattern[0])
        for tries in range(max_tries + 1):
            x = rng.randrange(0, self.H - h + 1)
            y = rng.randrange(0, self.W - w + 1)

            # Считаем живые в окне
            live = 0
            for i in range(h):
                for j in range(w):
                    live += self.g[x+i][y+j]

            # Если окно почти пустое — накладываем; иначе в конце — как есть
            if live <= 1 or tries == max_tries:
                for i in range(h):
                    for j in range(w):
                        self.g[x+i][y+j] = 1 if (self.g[x+i][y+j] or pattern[i][j]) else 0
                return x, y, (live <= 1)
        return 0, 0, False  

    def _count_neighbors(self, r: int, c: int) -> int:
        """Подсчёт 8 соседей; края не замкнуты (за пределами — 0)."""
        s = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:  # не считаем саму клетку
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.H and 0 <= cc < self.W:
                    s += self.g[rr][cc]
        return s

    def step(self) -> None:
        """Один шаг по правилам Конвея: рождение=3; выживание=2–3."""
        newg = [[0]*self.W for _ in range(self.H)]
        for i in range(self.H):
            for j in range(self.W):
                n = self._count_neighbors(i, j)
                if self.g[i][j] == 1:
                    newg[i][j] = 1 if (n == 2 or n == 3) else 0
                else:
                    newg[i][j] = 1 if n == 3 else 0
        self.g = newg

    def render(self) -> None:
        """Текстовая «визуализация» поля."""
        for row in self.g:
            print("".join(ALIVE if cell else DEAD for cell in row))
