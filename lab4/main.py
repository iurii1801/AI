#!/usr/bin/env python3
# Точка входа: парсим аргументы, готовим игру, запускаем симуляцию

import argparse, random, time
from utils import seed_from_student, random_density, clear_console
from game import Game
from patterns import GLIDER

def parse_args():
    ap = argparse.ArgumentParser(description="Lab 4: Game of Life (console, split files)")
    ap.add_argument("--size", type=int, default=40, help="Размер поля N=M (по варианту 40)")
    ap.add_argument("--density", type=float, default=None, help="Вероятность живой клетки (если не указана — случайно в [0.2..0.5])")
    ap.add_argument("--student", type=str, default="student", help="Строка для уникального seed (ФИО/группа)")
    ap.add_argument("--steps", type=int, default=300, help="Сколько шагов показать")
    ap.add_argument("--delay", type=float, default=0.06, help="Пауза между кадрами (сек.)")
    return ap.parse_args()

def main():
    args = parse_args()

    # Уникальность старта
    rng = random.Random(seed_from_student(args.student))
    # Плотность в требуемом диапазоне
    p_alive = args.density if args.density is not None else random_density(rng)

    N = args.size
    game = Game(N, N)                       # Поле N×N (40×40)
    game.random_init(p_alive, rng)          # Случайная начальная сетка
    gx, gy, free = game.place_pattern_safely(GLIDER, rng)  # Добавляем glider

    title = f"Game of Life | size={N}x{N} | density≈{p_alive:.2f} | glider@({gx},{gy}) free={free}"
    for step in range(args.steps):
        clear_console()                     # Очистка экрана
        print(f"{title} | step {step}")     # Номер шага 
        game.render()                       # Печатаем поле
        time.sleep(args.delay)              # Задержка для анимации
        game.step()                         # Применяем правила Конвея

if __name__ == "__main__":
    main()
