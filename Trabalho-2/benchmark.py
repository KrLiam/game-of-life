from main import sudoku
from timeit import timeit
import matplotlib.pyplot as plt



def f(n):
    def g():
        print("benchmark", n)
        return sudoku("input-sample.txt", n, 1)
    return g

def benchmark():
    por_processos = [
        timeit(f(n), number=5)
        for n in range(1, 11)
    ]

    plt.plot(range(1, 11), por_processos, "g")
    plt.show()


if __name__ == "__main__":
    benchmark()
