from argparse import ArgumentParser
from collections import namedtuple
from enum import Enum
from multiprocessing import Process, current_process
from threading import Lock
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
        regioes = [Test(i + 1, TestType.REGIAO, []) for i in range(9)]
        for i in range(9):
            for j in range(9):
                regioes[REGIOES[i, j]].elementos.append(matriz[i][j])

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
                    threads.append(f"T{i+1}: " + ", ".join(sorted(erros)))

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
    if num_threads > 81:
        num_threads = 81

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


# oi professor, isso aqui é para ganhar desempenho, já que é mais rápido acessar o hash map
# do que a thread ter que calcular a região de cada elemento
REGIOES = {
    (0, 0): 0,
    (0, 1): 0,
    (0, 2): 0,
    (0, 3): 1,
    (0, 4): 1,
    (0, 5): 1,
    (0, 6): 2,
    (0, 7): 2,
    (0, 8): 2,
    (1, 0): 0,
    (1, 1): 0,
    (1, 2): 0,
    (1, 3): 1,
    (1, 4): 1,
    (1, 5): 1,
    (1, 6): 2,
    (1, 7): 2,
    (1, 8): 2,
    (2, 0): 0,
    (2, 1): 0,
    (2, 2): 0,
    (2, 3): 1,
    (2, 4): 1,
    (2, 5): 1,
    (2, 6): 2,
    (2, 7): 2,
    (2, 8): 2,
    (3, 0): 3,
    (3, 1): 3,
    (3, 2): 3,
    (3, 3): 4,
    (3, 4): 4,
    (3, 5): 4,
    (3, 6): 5,
    (3, 7): 5,
    (3, 8): 5,
    (4, 0): 3,
    (4, 1): 3,
    (4, 2): 3,
    (4, 3): 4,
    (4, 4): 4,
    (4, 5): 4,
    (4, 6): 5,
    (4, 7): 5,
    (4, 8): 5,
    (5, 0): 3,
    (5, 1): 3,
    (5, 2): 3,
    (5, 3): 4,
    (5, 4): 4,
    (5, 5): 4,
    (5, 6): 5,
    (5, 7): 5,
    (5, 8): 5,
    (6, 0): 6,
    (6, 1): 6,
    (6, 2): 6,
    (6, 3): 7,
    (6, 4): 7,
    (6, 5): 7,
    (6, 6): 8,
    (6, 7): 8,
    (6, 8): 8,
    (7, 0): 6,
    (7, 1): 6,
    (7, 2): 6,
    (7, 3): 7,
    (7, 4): 7,
    (7, 5): 7,
    (7, 6): 8,
    (7, 7): 8,
    (7, 8): 8,
    (8, 0): 6,
    (8, 1): 6,
    (8, 2): 6,
    (8, 3): 7,
    (8, 4): 7,
    (8, 5): 7,
    (8, 6): 8,
    (8, 7): 8,
    (8, 8): 8,
}

if __name__ == "__main__":
    main()
