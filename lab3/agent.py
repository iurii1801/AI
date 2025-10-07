# Класс одного агента (птицы): позиция/скорость и один шаг обновления.
class Agent:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy

    def apply(self, ax, ay, vmax, W, H):
        # применяем управляющее «ускорение» от правил
        self.vx += ax
        self.vy += ay
        # ограничиваем максимальную скорость
        s = (self.vx*self.vx + self.vy*self.vy) ** 0.5
        if s > vmax and s > 0:
            k = vmax / s
            self.vx *= k
            self.vy *= k
        # обновляем позицию и зацикливаем по краям
        self.x = (self.x + self.vx) % W
        self.y = (self.y + self.vy) % H