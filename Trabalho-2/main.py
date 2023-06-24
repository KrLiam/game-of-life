from argparse import ArgumentParser
from multiprocessing import Process, current_process
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from functools import reduce


Matriz = list[list[int]]


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

        thread_items = [[] for _ in range(num_threads)]

        sets_linhas = [(set(), Lock()) for _ in range(9)]
        sets_colunas = [(set(), Lock()) for _ in range(9)]
        sets_regioes = [(set(), Lock()) for _ in range(9)]

        # dividir os itens para as threads
        for i in range(9):
            for j in range(9):
                thread_items[(9 * i + j) % num_threads].append((i, j))

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(
                    thread_funk,
                    matriz,
                    thread_items[n],
                    sets_linhas,
                    sets_colunas,
                    sets_regioes
                )
                for n in range(num_threads)
            ]

        results = [future.result() for future in futures]

        flat_results = reduce(lambda v, acc: acc.union(v), (s for s in results), set())
        erros_totais = len(flat_results)

        print(f"{current_process().name}: {erros_totais} erros encontrados ", end="")

        if erros_totais:
            print("(", end="")

            threads = []
            for i, erros in enumerate(results):
                if erros:
                    threads.append(f"T{i+1}: " + ", ".join(sorted(erros)))

            print("; ".join(threads), end=")")

        print()


def thread_funk(
    matriz: Matriz,
    thread_items: list[tuple[int, int]],
    sets_linhas,
    sets_colunas,
    sets_regioes,
):
    erros = set()

    for posicao in thread_items:
        regiao = REGIOES[posicao]
        i, j = posicao
        numero = matriz[i][j]

        with sets_linhas[i][1]:
            if numero not in sets_linhas[i][0]:
                sets_linhas[i][0].add(numero)
            else:
                erros.add(f'L{i+1}')

        with sets_colunas[i][1]:
            if numero not in sets_colunas[j][0]:
                sets_colunas[j][0].add(numero)
            else:
                erros.add(f'C{j+1}')

        with sets_regioes[regiao][1]:
            if numero not in sets_regioes[regiao][0]:
                sets_regioes[regiao][0].add(numero)
            else:
                erros.add(f'R{regiao+1}')

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
