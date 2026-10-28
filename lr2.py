"""
Лабораторная работа № 2. Вариант 19.
Эмпирический анализ временной сложности квадратичных сортировок.

Автор: Ситникова Ольга, группа БИ2-1.

Исходные данные варианта 19:
    размеры массивов n = 1000, 2000, 3000, 4000, 5000, 6000
    тип данных: N (почти упорядоченные: n/20 случайных перестановок пар)
    диапазон значений: [0; 50 000]
    число повторов k = 3 (берётся медиана)
    дополнительное задание М5: шейкерная сортировка (двунаправленный пузырёк)
    и её сравнение с классической сортировкой пузырьком

Запуск: python lr2.py   (для графиков нужен пакет matplotlib)
"""
import platform
import random
import statistics
import sys
import time

# ---------------------------------------------------------------------------
# Параметры варианта 19
# ---------------------------------------------------------------------------
SIZES = [1000, 2000, 3000, 4000, 5000, 6000]
KIND = "nearly_sorted"
LO, HI = 0, 50_000
REPEATS = 3
SEED = 42

if hasattr(sys.stdout, "reconfigure"):      # корректный вывод кириллицы в Windows
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Генерация данных и замер времени
# ---------------------------------------------------------------------------
def generate_data(n, kind="random", lo=0, hi=100_000, seed=SEED):
    """Генерирует массив длины n заданного типа (воспроизводимо, по seed)."""
    rng = random.Random(seed + n)
    data = [rng.randint(lo, hi) for _ in range(n)]
    if kind == "sorted":
        data.sort()
    elif kind == "reversed":
        data.sort(reverse=True)
    elif kind == "nearly_sorted":
        data.sort()
        for _ in range(max(1, n // 20)):              # ~5 % случайных перестановок
            i, j = rng.randrange(n), rng.randrange(n)
            data[i], data[j] = data[j], data[i]
    return data


def measure(sort_func, data, repeats=REPEATS):
    """Медианное время работы sort_func на данных data, с.

    Каждый раз сортируется копия data (функции исходный массив не меняют).
    Корректность результата проверяется по sorted() вне замера времени.
    """
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        times.append(time.perf_counter() - start)
        assert result == sorted(data), f"{sort_func.__name__}: ошибка сортировки"
    return statistics.median(times)


# ---------------------------------------------------------------------------
# Алгоритмы сортировки (исходный массив не изменяют)
# ---------------------------------------------------------------------------
def bubble_sort(arr):
    """Сортировка пузырьком с флагом досрочного выхода."""
    a = arr.copy()
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def shaker_sort(arr):
    """Шейкерная сортировка (двунаправленный пузырёк) с флагом выхода.

    Проход вправо выносит максимум в конец, проход влево выносит минимум
    в начало; границы неупорядоченной части [left, right] сужаются с обеих сторон.
    """
    a = arr.copy()
    left, right = 0, len(a) - 1
    while left < right:
        swapped = False
        for j in range(left, right):              # проход слева направо
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        right -= 1
        if not swapped:
            break
        swapped = False
        for j in range(right, left, -1):          # проход справа налево
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                swapped = True
        left += 1
        if not swapped:
            break
    return a


def insertion_sort(arr):
    """Сортировка вставками."""
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


# ---------------------------------------------------------------------------
# Версии с подсчётом операций (только для анализа, в замере времени не участвуют)
# ---------------------------------------------------------------------------
def bubble_sort_counted(arr):
    """Возвращает (сравнений, обменов, проходов) для сортировки пузырьком."""
    a = arr.copy()
    n = len(a)
    comparisons = swaps = passes = 0
    for i in range(n - 1):
        swapped = False
        passes += 1
        for j in range(n - 1 - i):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return comparisons, swaps, passes


def shaker_sort_counted(arr):
    """Возвращает (сравнений, обменов, проходов) для шейкерной сортировки."""
    a = arr.copy()
    left, right = 0, len(a) - 1
    comparisons = swaps = passes = 0
    while left < right:
        swapped = False
        passes += 1
        for j in range(left, right):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        right -= 1
        if not swapped:
            break
        swapped = False
        passes += 1
        for j in range(right, left, -1):
            comparisons += 1
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                swaps += 1
                swapped = True
        left += 1
        if not swapped:
            break
    return comparisons, swaps, passes


def insertion_sort_counted(arr):
    """Возвращает (сравнений, сдвигов, проходов) для сортировки вставками."""
    a = arr.copy()
    comparisons = shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] <= key:
                break
            a[j + 1] = a[j]
            shifts += 1
            j -= 1
        a[j + 1] = key
    return comparisons, shifts, max(0, len(a) - 1)


# ---------------------------------------------------------------------------
# Вывод и графики
# ---------------------------------------------------------------------------
def print_system_info():
    """Характеристики вычислительной системы (для отчёта)."""
    print("Характеристики системы:")
    print(f"  ОС:        {platform.platform()}")
    print(f"  Процессор: {platform.processor() or 'не определён'}")
    print(f"  Python:    {platform.python_version()}")
    print()


def print_tables(results):
    names = list(results)
    print(f"Тип данных: почти упорядоченные, диапазон [{LO}; {HI}], "
          f"k = {REPEATS}, seed = {SEED}\n")

    print("Таблица 1. Медианное время сортировки, с")
    print(f"{'n':>6}" + "".join(f"{name:>14}" for name in names))
    for idx, n in enumerate(SIZES):
        print(f"{n:>6}" + "".join(f"{results[name][idx]:>14.4f}" for name in names))
    print()

    print("Таблица 2. Отношение T(n)/n^2 (x 1e-9, с)")
    print(f"{'n':>6}" + "".join(f"{name:>14}" for name in names))
    for idx, n in enumerate(SIZES):
        print(f"{n:>6}" + "".join(f"{results[name][idx] / n**2 * 1e9:>14.2f}" for name in names))
    print()

    print("Таблица 3. Проверка квадратичного роста: T(2n)/T(n)")
    print(f"{'Переход':>14}" + "".join(f"{name:>14}" for name in names) + f"{'Теория':>10}")
    for n in SIZES:
        if 2 * n in SIZES:
            i, j = SIZES.index(n), SIZES.index(2 * n)
            row = f"{f'{n} -> {2 * n}':>14}"
            row += "".join(f"{results[name][j] / results[name][i]:>14.2f}" for name in names)
            print(row + f"{4:>10}")
    print()

    print("Таблица 4. Отношение времени (пузырёк / вставки) и (пузырёк / шейкер)")
    print(f"{'n':>6}{'пузырёк/вставки':>18}{'пузырёк/шейкер':>18}")
    for idx, n in enumerate(SIZES):
        b, s, ins = (results["Пузырьком"][idx], results["Шейкерная"][idx],
                     results["Вставками"][idx])
        print(f"{n:>6}{b / ins:>18.2f}{b / s:>18.2f}")
    print()


def count_operations():
    """Число сравнений, обменов (сдвигов) и проходов для каждого размера n."""
    counters = {
        "Пузырьком": bubble_sort_counted,
        "Шейкерная": shaker_sort_counted,
        "Вставками": insertion_sort_counted,
    }
    return {name: [f(generate_data(n, KIND, LO, HI)) for n in SIZES]
            for name, f in counters.items()}


def print_operations(ops):
    names = list(ops)
    for title, idx in (("Таблица 5. Число сравнений", 0),
                       ("Таблица 6. Число обменов (для вставок — сдвигов)", 1),
                       ("Таблица 7. Число проходов по массиву", 2)):
        print(title)
        ref_head = f"{'n^2/2':>14}" if idx == 0 else ""
        print(f"{'n':>6}" + "".join(f"{name:>14}" for name in names) + ref_head)
        for k, n in enumerate(SIZES):
            ref = f"{n * n // 2:>14}" if idx == 0 else ""
            print(f"{n:>6}" + "".join(f"{ops[name][k][idx]:>14}" for name in names) + ref)
        print()


def make_plots(results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен: графики не построены (pip install matplotlib)")
        return

    # График 1: пузырёк и вставки на одних осях
    plt.figure(figsize=(8, 5))
    for name in ("Пузырьком", "Вставками"):
        plt.plot(SIZES, results[name], marker="o", label=name)
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с")
    plt.title("Почти упорядоченные данные: пузырёк и вставки")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("lr2_plot.png", dpi=150)
    plt.close()

    # График 2 (М5): пузырёк и шейкерная сортировка
    plt.figure(figsize=(8, 5))
    for name in ("Пузырьком", "Шейкерная"):
        plt.plot(SIZES, results[name], marker="o", label=name)
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с")
    plt.title("М5. Сортировка пузырьком и шейкерная сортировка")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("lr2_plot_m5.png", dpi=150)
    plt.close()
    print("Графики сохранены: lr2_plot.png, lr2_plot_m5.png")


def main():
    algorithms = {
        "Пузырьком": bubble_sort,
        "Шейкерная": shaker_sort,
        "Вставками": insertion_sort,
    }
    print_system_info()
    results = {name: [] for name in algorithms}
    for n in SIZES:
        data = generate_data(n, KIND, LO, HI)        # один массив для всех алгоритмов
        for name, func in algorithms.items():
            results[name].append(measure(func, data, REPEATS))
    print_tables(results)
    print_operations(count_operations())
    make_plots(results)


if __name__ == "__main__":
    main()
