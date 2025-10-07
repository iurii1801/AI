# Утилиты: seed из строки, случайная плотность, очистка экрана

import hashlib, os, random

def seed_from_student(student: str) -> int:
    """Стабильный seed из строки студента (SHA-256 → int)."""
    h = hashlib.sha256(student.encode("utf-8")).hexdigest()
    return int(h[:16], 16) & 0x7FFFFFFF

def random_density(rng: random.Random) -> float:
    """Плотность живых клеток в [0.2..0.5] по условию лабы."""
    return rng.uniform(0.2, 0.5)

def clear_console() -> None:
    """Кроссплатформенная очистка консоли."""
    os.system("cls" if os.name == "nt" else "clear")
