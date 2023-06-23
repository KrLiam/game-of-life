from argparse import ArgumentParser


def sudoku(arquivo: str, processos: int, threads: int):
    ...


def main():
    parser = ArgumentParser()

    parser.add_argument("arquivo_solucoes")
    parser.add_argument("processos")
    parser.add_argument("threads")

    args = parser.parse_args()

    sudoku(args.arquivo_solucoes, args.processos, args.threads)

if __name__ == "__main__":
    main()

    