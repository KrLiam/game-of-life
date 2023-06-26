from main import sudoku
from timeit import timeit
import matplotlib.pyplot as plt



def f(n):
    def g():
        print("benchmark", n)
        return sudoku("input-sample.txt", n, 1)
    return g

def benchmark():
    RANGE = list(range(1, 11))
    NUM_THREADS = 1
    NUM_PROCESSOS = 4
    NUMBER = 5

    por_processos = [
        timeit(lambda: sudoku("input-sample.txt", n, NUM_THREADS), number=NUMBER)
        for n in RANGE
    ]
    por_threads = [
        timeit(lambda: sudoku("input-sample.txt", NUM_PROCESSOS, n), number=NUMBER)
        for n in RANGE
    ]

    speedup_por_processos = [por_processos[0] / n for n in por_processos]
    speedup_por_threads = [por_processos[0] / n for n in por_threads]

    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.set_title(f"{RANGE[0]}-{RANGE[-1]} Processos, {NUM_THREADS} thread")
    ax1.plot(RANGE, speedup_por_processos, "r")
    ax1.set_xbound(RANGE[0], RANGE[-1])
    ax1.set_xlabel("Número de Processos")
    ax1.set_ylabel("Speedup")

    ax2.set_title(f"{NUM_PROCESSOS} Processos, {RANGE[0]}-{RANGE[-1]} threads")
    ax2.plot(RANGE, speedup_por_threads, "r")
    ax2.set_xbound(RANGE[0], RANGE[-1])
    ax2.set_xlabel("Número de Threads")
    ax2.set_ylabel("Speedup")

    plt.show()



if __name__ == "__main__":
    benchmark()
