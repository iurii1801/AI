import random
import math
import matplotlib.pyplot as plt

L = 4  # длина хромосомы

# Целевая функция (вариант 1)
# f(x) = x * sin(6πx) + 0.5 * cos(4πx) + 1
def f(x):
    return x * math.sin(6 * math.pi * x) + 0.5 * math.cos(4 * math.pi * x) + 1


# Перевод двоичной строки длиной 4 бита в число x ∈ [0, 1]
def decode(bits):
    return int(bits, 2) / (2 ** L - 1)


# Ввод параметров от пользователя
N = int(input("Размер популяции N (по умолчанию 4): ") or 4)
pc = float(input("Вероятность кроссовера pc (по умолчанию 0.8): ") or 0.8)
pm = float(input("Вероятность мутации pm (по умолчанию 0.05): ") or 0.05)
G = int(input("Количество поколений G (по умолчанию 30): ") or 30)
if G < 30:
    print("G меньше 30, установлено значение 30.")
    G = 30

# Создание начальной популяции
# Каждая хромосома состоит из 4 случайных битов
population = ["".join(random.choice("01") for _ in range(L)) for _ in range(N)]

best_f_history = []  # здесь будут храниться максимальные значения f(x) для графика

print("\nГЕНЕТИЧЕСКИЙ АЛГОРИТМ")
print(f"N={N}, pc={pc}, pm={pm}, G={G}, L={L}")

# Основной цикл по поколениям
for g in range(G):
    # Перевод хромосом в x и вычисление функции f(x)
    xs = [decode(ch) for ch in population]
    fs = [f(x) for x in xs]

    # Поиск статистики текущего поколения
    f_max = max(fs)
    f_min = min(fs)
    f_avg = sum(fs) / N
    x_best = xs[fs.index(f_max)]
    best_f_history.append(f_max)

    # Вывод информации о поколении
    print(f"\nПоколение {g}")
    print("№  хромосома   x       f(x)")
    for i, (ch, xv, fv) in enumerate(zip(population, xs, fs), start=1):
        print(f"{i:2d}  {ch}   {xv:6.3f}  {fv:8.4f}")
    print(f"max={f_max:.4f}, min={f_min:.4f}, avg={f_avg:.4f}")
    print(f"Лучший x = {x_best:.4f}")

    # Создание нового поколения
    new_population = []

    # Выбираем двух лучших родителей по значению функции
    idx_sorted = sorted(range(N), key=lambda i: fs[i], reverse=True)
    p1 = population[idx_sorted[0]]
    p2 = population[idx_sorted[1]]

    while len(new_population) < N:
        print(f"\nРодители: {p1}, {p2}")

        # Кроссовер (обмен участками хромосом)
        if random.random() < pc:
            point = random.randint(1, L - 1)
            c1 = p1[:point] + p2[point:]
            c2 = p2[:point] + p1[point:]
            print(f"Кроссовер в точке {point}: {c1}, {c2}")
        else:
            c1, c2 = p1, p2
            print("Кроссовер не выполнен")

        # Мутация (изменение отдельных битов)
        c1_list = list(c1)
        c2_list = list(c2)
        for i in range(L):
            if random.random() < pm:
                old = c1_list[i]
                c1_list[i] = "1" if old == "0" else "0"
                print(f"Мутация: у 1-го потомка бит {i} {old}->{c1_list[i]}")
            if random.random() < pm:
                old = c2_list[i]
                c2_list[i] = "1" if old == "0" else "0"
                print(f"Мутация: у 2-го потомка бит {i} {old}->{c2_list[i]}")

        c1 = "".join(c1_list)
        c2 = "".join(c2_list)

        # Добавляем потомков в новое поколение
        new_population.append(c1)
        if len(new_population) < N:
            new_population.append(c2)

    # Обновляем популяцию
    population = new_population

# После всех поколений ищем лучший результат
xs = [decode(ch) for ch in population]
fs = [f(x) for x in xs]
f_max = max(fs)
x_best = xs[fs.index(f_max)]

print("\nРЕЗУЛЬТАТ")
print(f"Лучшее найденное x* = {x_best:.4f}")
print(f"f(x*) = {f_max:.4f}")

# Вывод таблицы последнего поколения
print("\nПоследнее поколение:")
print("№  хромосома   x       f(x)")
for i, (ch, xv, fv) in enumerate(zip(population, xs, fs), start=1):
    print(f"{i:2d}  {ch}   {xv:6.3f}  {fv:8.4f}")

# Построение графика изменения максимального значения функции
plt.plot(range(G), best_f_history, marker="o")
plt.xlabel("Поколение")
plt.ylabel("max f(x)")
plt.title("Изменение максимального значения f(x) по поколениям")
plt.grid(True)
plt.show()
