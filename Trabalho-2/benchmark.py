from argparse import ArgumentParser
import json
from pathlib import Path
from main import sudoku, ler_solucoes
from timeit import timeit
import matplotlib.pyplot as plt


def f(arquivo: str, processos: int, threads: int):
    def g():
        print(f"benchmark {processos=} {threads=}")
        return sudoku(arquivo, processos, threads)

    return g


BENCHMARK_JSON = Path.cwd() / "benchmark.json"

def benchmark(
    arquivo: str,
    intervalo_max: int,
    iteracoes: int,
    num_fixo_processos: int = 4,
    num_fixo_threads: int = 1,
    merge: bool = False,
):
    solucoes = ler_solucoes(arquivo)
    intervalo = list(range(1, intervalo_max + 1))

    por_processos = [
        timeit(f(arquivo, n, num_fixo_threads), number=iteracoes) for n in intervalo
    ]
    por_threads = [
        timeit(f(arquivo, num_fixo_processos, n), number=iteracoes) for n in intervalo
    ]

    if merge:
        try:
            txt = BENCHMARK_JSON.read_text()
        except FileNotFoundError:
            txt = "{}"
        
        data = json.loads(txt)
        iteracoes += data.get("iterations", 0)
        benchmarks = data.get("benchmarks", [{}, {}])
        prev_por_processos = benchmarks[0].get("tempo", [0] * len(por_processos))
        prev_por_threads = benchmarks[1].get("tempo", [0] * len(por_threads))
        por_processos = [a + b for a, b in zip(por_processos, prev_por_processos)]
        por_threads = [a + b for a, b in zip(por_threads, prev_por_threads)]

    speedup_por_processos = [por_processos[0] / n for n in por_processos]
    speedup_por_threads = [por_threads[0] / n for n in por_threads]

    data = {
        "input_size": len(solucoes),
        "iterations": iteracoes,
        "benchmarks": [
            {
                "processos": intervalo,
                "threads": num_fixo_threads,
                "tempo": por_processos,
                "speedup": speedup_por_processos,
            },
            {
                "processos": num_fixo_processos,
                "threads": intervalo,
                "tempo": por_threads,
                "speedup": speedup_por_threads,
            },
        ],
    }
    BENCHMARK_JSON.write_text(json.dumps(data, indent=4))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(12, 5)

    ax1.set_title(
        f"{intervalo[0]}-{intervalo[-1]} Processos, {num_fixo_threads} thread"
    )
    ax1.plot(intervalo, speedup_por_processos, "r")
    ax1.set_xbound(intervalo[0], intervalo[-1])
    ax1.xaxis.get_major_locator().set_params(integer=True)
    ax1.set_xlabel("Número de Processos")
    ax1.set_ylabel("Speedup")

    ax2.set_title(
        f"{num_fixo_processos} Processos, {intervalo[0]}-{intervalo[-1]} threads"
    )
    ax2.plot(intervalo, speedup_por_threads, "r")
    ax2.set_xbound(intervalo[0], intervalo[-1])
    ax2.xaxis.get_major_locator().set_params(integer=True)
    ax2.set_xlabel("Número de Threads")
    ax2.set_ylabel("Speedup")

    # plt.show()
    plt.savefig("benchmark.png", bbox_inches="tight")


def main():
    parser = ArgumentParser()

    parser.add_argument("arquivo_solucoes")
    parser.add_argument("intervalo_max", type=int, default=10)
    parser.add_argument("iteracoes", type=int, default=1)
    parser.add_argument("--merge", action="store_true", default=False, help="Acumula resultados obtidos com os dados já presentes no arquivo benchmark.json")

    args = parser.parse_args()

    benchmark(
        args.arquivo_solucoes,
        args.intervalo_max,
        args.iteracoes,
        merge=args.merge,
    )


if __name__ == "__main__":
    main()
