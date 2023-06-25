from argparse import ArgumentParser
from enum import Enum
from multiprocessing import Process, current_process
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from typing import NamedTuple


Matriz = list[list[int]]


class TestType(Enum):
    LINHA = "L"
    COLUNA = "C"
    REGIAO = "R"


class Test(NamedTuple):
    i: int
    tipo: TestType
    elementos: list[int]


ORDEM_PRINT = {TestType.LINHA.value: 0, TestType.COLUNA.value: 1, TestType.REGIAO.value: 2}


POSICOES: dict[int, tuple[tuple[int, int]]] = {
    0: ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)),
    1: ((0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)),
    2: ((0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 6), (2, 7), (2, 8)),
    3: ((3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)),
    4: ((3, 3), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)),
    5: ((3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)),
    6: ((6, 0), (6, 1), (6, 2), (7, 0), (7, 1), (7, 2), (8, 0), (8, 1), (8, 2)),
    7: ((6, 3), (6, 4), (6, 5), (7, 3), (7, 4), (7, 5), (8, 3), (8, 4), (8, 5)),
    8: ((6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)),
}


def ler_solucoes(arquivo: str) -> list[Matriz]:
    with open(arquivo, "rt") as f:
        txt = f.read()

    boards = txt.split("\n\n")

    for i, board in enumerate(boards):
        matriz = [[int(x) for x in line] for line in board.split("\n")]
        boards[i] = (i + 1, matriz)

    return boards


def processo_funk(num_threads: int, matrizes: tuple[str, Matriz]):
    for numero, matriz in matrizes:
        print(f"{current_process().name}: resolvendo quebra-cabeças {numero}")

        linhas = [Test(i + 1, TestType.LINHA, linha) for i, linha in enumerate(matriz)]
        colunas = [
            Test(i + 1, TestType.COLUNA, [linha[i] for linha in matriz])
            for i in range(9)
        ]
        regioes = [Test(k + 1, TestType.REGIAO, [matriz[i][j] for i, j in POSICOES[k]]) for k in range(9)]

        testes = linhas + colunas + regioes

        thread_items = [[] for _ in range(num_threads)]
        for i in range(len(testes)):
            thread_items[i % num_threads].append(testes[i])

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(thread_funk, thread_items[n])
                for n in range(num_threads)
            ]

        results = [future.result() for future in futures]

        flat_results = reduce(lambda v, acc: acc.union(v), (s for s in results), set())
        erros_totais = len(flat_results)

        msg = f"{current_process().name}: {erros_totais} erros encontrados "

        if erros_totais:
            threads = []
            for i, erros in enumerate(results):
                if erros:
                    threads.append(f"T{i+1}: " + ", ".join(sorted(erros, key=lambda x: ORDEM_PRINT[x[0]])))

            msg += "(" + "; ".join(threads) + ")"

        print(msg)


def thread_funk(testes: list[Test]):
    erros = set()

    for i, tipo, elementos in testes:
        if len(set(elementos)) != 9:
            erros.add(tipo.value + str(i))

    return erros


def sudoku(arquivo: str, num_processos: int, num_threads: int):
    solucoes = ler_solucoes(arquivo)

    if num_processos <= 0:
        print("O número de processos deve ser maior que 0!")
        return
    if num_processos > len(solucoes):
        num_processos = len(solucoes)

    if num_threads <= 0:
        print("O número de threads deve ser maior que 0!")
        return
    if num_threads > 27:
        num_threads = 27

    proc_tabuleiros = [[] for i in range(num_processos)]
    for i in range(len(solucoes)):
        proc_tabuleiros[i % num_processos].append(solucoes[i])

    processos = [
        Process(
            name=f"Processo {i+1}",
            target=processo_funk,
            args=(num_threads, proc_tabuleiros[i]),
        )
        for i in range(num_processos)
    ]
    for processo in processos:
        processo.start()
    for processo in processos:
        processo.join()


def main():
    parser = ArgumentParser()

    parser.add_argument("arquivo_solucoes")
    parser.add_argument("processos", type=int)
    parser.add_argument("threads", type=int)

    args = parser.parse_args()

    sudoku(args.arquivo_solucoes, args.processos, args.threads)


if __name__ == "__main__":
    main()
