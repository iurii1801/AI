# fuzzy_weather_app.py
# ЛР 5.1 — Прогнозирование вероятности осадков с помощью нечёткой логики (Мамдани)
# Модель оценивает вероятность осадков по температуре, влажности и давлению.
# Используются треугольные функции принадлежности, 27 правил Мамдани
# и дефаззификация методом центра тяжести. Интерфейс сделан на Streamlit.

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


# Функция треугольной принадлежности:
# возвращает число от 0 до 1, показывающее, насколько значение x
# принадлежит терму (a, b, c). Применяется для low, medium, high.
def tri(x, a, b, c):
    x = np.asarray(x, float)
    left = (x - a) / (b - a + 1e-9)
    right = (c - x) / (c - b + 1e-9)
    y = np.minimum(left, right)
    y = np.where((x < a) | (x > c), 0, y)
    y = np.where(x == b, 1.0, y)
    return np.clip(y, 0, 1)


# Функция создаёт три терма (низкий, средний, высокий) для диапазона 0–100.
# Эти термы используются для всех переменных (температура, влажность, давление).
def terms():
    return {
        "low":    lambda v: tri(v, 0, 0, 50),
        "medium": lambda v: tri(v, 25, 50, 75),
        "high":   lambda v: tri(v, 50, 100, 100)
    }


# Универсумы и функции принадлежности для входов и выхода.
# X и Y — оси для расчётов и построения графиков.
X = np.linspace(0, 100, 501)
Y = np.linspace(0, 100, 501)
T = terms()   # температура
H = terms()   # влажность
P = terms()   # давление
R = terms()   # выход (вероятность осадков)
LABS = ["low", "medium", "high"]


# Логика определения результата по трём входам (t,h,p):
# влажность ↑ и давление ↓ увеличивают вероятность осадков,
# низкая температура тоже немного увеличивает.
def cons(t, h, p):
    score = 0
    score += 2 if h == "high" else 1 if h == "medium" else 0
    score += 2 if p == "low"  else 1 if p == "medium" else 0
    score += 1 if t == "low"  else 0 if t == "medium" else -1
    return "high" if score >= 3 else ("medium" if score >= 1 else "low")


# Формируем все 27 правил Мамдани (3×3×3 комбинации входов).
RULES = [(t, h, p, cons(t, h, p)) for t in LABS for h in LABS for p in LABS]


# Главная функция нечёткого вывода (по Мамдани).
# Выполняет все этапы:
# 1. Фаззификация — перевод чисел в степени принадлежности.
# 2. Применение правил — вычисление силы срабатывания (min).
# 3. Агрегация — объединение всех выходных функций (max).
# 4. Дефаззификация — расчёт центра тяжести для получения числа.
def infer(temp, hum, pres):
    muT = {k: float(T[k](temp)) for k in LABS}
    muH = {k: float(H[k](hum))  for k in LABS}
    muP = {k: float(P[k](pres)) for k in LABS}

    agg = np.zeros_like(Y)
    fired = []

    for (t, h, p, r) in RULES:
        alpha = min(muT[t], muH[h], muP[p])
        if alpha <= 0:
            continue
        fired.append(((t, h, p, r), alpha))
        agg = np.maximum(agg, np.minimum(alpha, R[r](Y)))

    area = np.trapz(agg, Y)
    crisp = np.trapz(Y * agg, Y) / area if area > 1e-12 else 0
    return crisp, agg, fired


# Интерфейс Streamlit: слайдеры, вывод результата и графики.
st.set_page_config(page_title="Fuzzy Weather", layout="centered")
st.title("ЛР 5.1 — Вероятность осадков (нечёткая логика Мамдани)")

col1, col2 = st.columns(2)
with col1:
    t = st.slider("Температура (0–100)", 0, 100, 40)
    h = st.slider("Влажность (0–100)",   0, 100, 80)
with col2:
    p = st.slider("Давление (0–100)",    0, 100, 30)

# Расчёт результата
crisp, agg, fired = infer(t, h, p)
st.subheader(f"Вероятность осадков: **{crisp:.1f}%**")

# Текстовая интерпретация результата
st.info("Оценка: " + ("низкая" if crisp < 33.3 else "средняя" if crisp < 66.6 else "высокая"))

# Отображение сработавших правил
with st.expander("Сработавшие правила"):
    for (t_, h_, p_, r_), a in sorted(fired, key=lambda x: x[1], reverse=True)[:10]:
        st.write(f"ЕСЛИ T={t_}, H={h_}, P={p_} → R={r_}  (α={a:.2f})")


# Отдельная функция для построения графиков функций принадлежности.
def show_mf(x, fns, title):
    fig, ax = plt.subplots()
    ax.plot(x, fns["low"](x), label="low")
    ax.plot(x, fns["medium"](x), label="medium")
    ax.plot(x, fns["high"](x), label="high")
    ax.set_title(title)
    ax.set_xlabel("0–100")
    ax.set_ylabel("µ (степень принадлежности)")
    ax.legend()
    st.pyplot(fig)


# Визуализация функций принадлежности входных переменных
st.subheader("Функции принадлежности (входные)")
show_mf(X, T, "Температура")
show_mf(X, H, "Влажность")
show_mf(X, P, "Давление")

# Визуализация выходной переменной (до и после агрегации)
st.subheader("Выходная функция (вероятность осадков)")
fig2, ax2 = plt.subplots()
ax2.plot(Y, R["low"](Y), label="low (эталон)")
ax2.plot(Y, R["medium"](Y), label="medium (эталон)")
ax2.plot(Y, R["high"](Y), label="high (эталон)")
ax2.plot(Y, agg, label="агрегированный выход", linewidth=2, color="red")
ax2.set_xlabel("0–100%")
ax2.set_ylabel("µ")
ax2.legend()
st.pyplot(fig2)

st.caption("Модель Мамдани: AND=min, импликация=обрезка, агрегация=max, дефаззификация=центроид.")
