#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from agent import Agent

# параметры модели
W, H = 100, 100          # размеры плоскости
N = 60                   # число агентов
RADIUS = 15.0            # радиус поиска соседей
SEP = 8.0                # дистанция для «разделения» (анти-столкновения)
MAX_SPEED = 2.5          # максимальная скорость
WC, WA, WS = 0.01, 0.05, 0.10  # веса правил: cohesion / alignment / separation
STEER_LIMIT = 0.5        # мягкий лимит ускорения (сглаживает повороты)

random.seed(0)           # фиксируем случайность для воспроизводимых запусков

# инициализация стаи: случайные позиции и скорости
agents = []
for _ in range(N):
    ang = random.uniform(0, 2*math.pi)
    spd = random.uniform(0.5*MAX_SPEED, MAX_SPEED)
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    agents.append(Agent(x, y, math.cos(ang)*spd, math.sin(ang)*spd))

def neighbors(i):
    """Возвращает индексы соседей агента i в радиусе RADIUS (евклидово расстояние)."""
    xi, yi = agents[i].x, agents[i].y
    n = []
    for j, a in enumerate(agents):
        if j == i:
            continue
        if math.hypot(xi - a.x, yi - a.y) <= RADIUS:
            n.append(j)
    return n

def step():
    """Один шаг модели: считаем три вектора для каждого агента и обновляем состояние."""
    ax = [0.0]*N
    ay = [0.0]*N
    for i in range(N):
        nb = neighbors(i)
        if not nb:
            continue

        # cohesion — вектор к центру масс соседей
        cx = sum(agents[j].x for j in nb)/len(nb) - agents[i].x
        cy = sum(agents[j].y for j in nb)/len(nb) - agents[i].y

        # alignment — вектор к средней скорости соседей
        avx = sum(agents[j].vx for j in nb)/len(nb) - agents[i].vx
        avy = sum(agents[j].vy for j in nb)/len(nb) - agents[i].vy

        # separation — отталкивание от слишком близких
        sx = sy = 0.0
        xi, yi = agents[i].x, agents[i].y
        for j in nb:
            dx = xi - agents[j].x
            dy = yi - agents[j].y
            d = math.hypot(dx, dy)
            if 0 < d < SEP:
                sx += dx/d
                sy += dy/d

        # взвешенная сумма трёх эффектов
        ax[i] = WC*cx + WA*avx + WS*sx
        ay[i] = WC*cy + WA*avy + WS*sy

        # мягкое ограничение мгновенного «поворота» (ускорения)
        a = math.hypot(ax[i], ay[i])
        if a > STEER_LIMIT and a > 0:
            k = STEER_LIMIT / a
            ax[i] *= k
            ay[i] *= k

    # применяем ускорения ко всем агентам (ограничение скорости и wrap внутри Agent.apply)
    for i in range(N):
        agents[i].apply(ax[i], ay[i], MAX_SPEED, W, H)

# визуализация (Matplotlib)
fig, axp = plt.subplots(figsize=(6, 6))
axp.set_xlim(0, W)
axp.set_ylim(0, H)
axp.set_aspect('equal')
axp.set_title('Boids — Лаба ИИ №3')

dots = axp.scatter([a.x for a in agents], [a.y for a in agents], s=22)

def update(_):
    """Колбэк анимации: шаг модели + обновление точек."""
    step()
    dots.set_offsets([(a.x, a.y) for a in agents])
    return dots,

if __name__ == '__main__':
    anim = FuncAnimation(fig, update, interval=35, blit=False, cache_frame_data=False)
    plt.show()