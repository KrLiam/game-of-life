from argparse import ArgumentParser
from multiprocessing import Process, Pipe, current_process
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


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

        sets_linhas = [set() for _ in range(9)]
        sets_colunas = [set() for _ in range(9)]
        sets_regioes = [set() for _ in range(9)]

        # dividir os itens para as threads
        for i in range(9):
            for j in range(9):
                thread_items[(9 * i + j) % num_threads].append((i, j))

        set_erros = set()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(
                    thread_funk,
                    thread_items[n],
                    sets_regioes,
                    sets_linhas,
                    sets_colunas,
                    matriz,
                    set_erros
                )
                for n in range(num_threads)
            ]

        results = [future.result() for future in futures]

        erros_totais = sum(sum(len(s) for s in thread) for thread in results)

        print(f"{current_process().name}: {erros_totais} erros encontrados ", end="")

        if erros_totais:
            print("(", end="")

            threads = []
            for i, (linhas, colunas, regioes) in enumerate(results):
                l = (f"L{n+1}" for n in linhas)
                c = (f"C{n+1}" for n in colunas)
                r = (f"R{n+1}" for n in regioes)

                thread_erros = (*l, *c, *r)
                if thread_erros:
                    threads.append(f"T{i+1}: " + ", ".join(thread_erros))

            print("; ".join(threads), end=")")

        print()


def thread_funk(
    thread_items: list[tuple[int, int]],
    sets_regioes: list[set[int]],
    sets_linhas: list[set[int]],
    sets_colunas: list[set[int]],
    matriz: Matriz,
    set_erros: set
):
    linhas_com_erro = set()
    colunas_com_erro = set()
    regioes_com_erro = set()

    for posicao in thread_items:
        i, j = posicao
        regiao = REGIOES[posicao]

        if (f"L{i + 1}" not in set_erros) and (f"C{j + 1}" not in set_erros) and (f"R{regiao + 1}" not in set_erros):
            numero = matriz[i][j]

            size_l = len(sets_linhas[i])
            size_c = len(sets_colunas[j])
            size_r = len(sets_regioes[regiao])

            sets_linhas[i].add(numero)
            sets_colunas[j].add(numero)
            sets_regioes[regiao].add(numero)

            if len(sets_linhas[i]) == size_l:
                linhas_com_erro.add(i)
                set_erros.add(f"L{i + 1}")
            if len(sets_colunas[j]) == size_c:
                colunas_com_erro.add(j)
                set_erros.add(f"C{j + 1}")
            if len(sets_regioes[regiao]) == size_r:
                regioes_com_erro.add(regiao)
                set_erros.add(f"R{regiao + 1}")

    return linhas_com_erro, colunas_com_erro, regioes_com_erro


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
        processo.join


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
