from main import sudoku
from timeit import timeit
import matplotlib.pyplot as plt


RANGE = list(range(1, 11))
NUM_THREADS = 1
NUM_PROCESSOS = 4
NUMBER = 5
INPUT_NAME = "input-sample-big.txt"

def f(processos, threads):
    def g():
        print(f"benchmark {processos=} {threads=}")
        return sudoku(INPUT_NAME, processos, threads)
    return g

def benchmark():

    por_processos = [
        timeit(f(n, NUM_THREADS), number=NUMBER)
        for n in RANGE
    ]
    por_threads = [
        timeit(f(NUM_PROCESSOS, n), number=NUMBER)
        for n in RANGE
    ]

    speedup_por_processos = [por_processos[0] / n for n in por_processos]
    speedup_por_threads = [por_threads[0] / n for n in por_threads]

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(12, 5)

    ax1.set_title(f"{RANGE[0]}-{RANGE[-1]} Processos, {NUM_THREADS} thread")
    ax1.plot(RANGE, speedup_por_processos, "r")
    ax1.set_xbound(RANGE[0], RANGE[-1])
    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.set_xlabel("Número de Processos")
    ax1.set_ylabel("Speedup")

    ax2.set_title(f"{NUM_PROCESSOS} Processos, {RANGE[0]}-{RANGE[-1]} threads")
    ax2.plot(RANGE, speedup_por_threads, "r")
    ax2.set_xbound(RANGE[0], RANGE[-1])
    ax2.xaxis.get_major_locator().set_params(integer=True)
    ax2.set_xlabel("Número de Threads")
    ax2.set_ylabel("Speedup")

    # plt.show()
    plt.savefig("benchmark.png")



if __name__ == "__main__":
    benchmark()
