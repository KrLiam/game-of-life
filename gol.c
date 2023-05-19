/*
 * The Game of Life
 *
 * RULES:
 *  1. A cell is born, if it has exactly three neighbours.
 *  2. A cell dies of loneliness, if it has less than two neighbours.
 *  3. A cell dies of overcrowding, if it has more than three neighbours.
 *  4. A cell survives to the next generation, if it does not die of lonelines or overcrowding.
 *
 * In this version, a 2D array of ints is used.  A 1 cell is on, a 0 cell is off.
 * The game plays a number of steps (given by the input), printing to the screen each time.
 * A 'x' printed means on, space means off.
 *
 */

#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include "gol.h"

/* Statistics */
stats_t statistics;

cell_t **allocate_board(int size)
{
    cell_t **board = (cell_t **)malloc(sizeof(cell_t *) * size);
    int i;
    for (i = 0; i < size; i++)
        board[i] = (cell_t *)malloc(sizeof(cell_t) * size);
    
    statistics.borns = 0;
    statistics.survivals = 0;
    statistics.loneliness = 0;
    statistics.overcrowding = 0;

    return board;
}

void free_board(cell_t **board, int size)
{
    int i;
    for (i = 0; i < size; i++)
        free(board[i]);
    free(board);
}

int adjacent_to(cell_t **board, int size, int i, int j)
{
    int k, l, count = 0;

    int sk = (i > 0) ? i - 1 : i;
    int ek = (i + 1 < size) ? i + 1 : i;
    int sl = (j > 0) ? j - 1 : j;
    int el = (j + 1 < size) ? j + 1 : j;

    for (k = sk; k <= ek; k++)
        for (l = sl; l <= el; l++)
            count += board[k][l];
    count -= board[i][j];

    return count;
}

int g_n_threads;
int g_size;
cell_t** g_board;
cell_t** g_newboard;

pthread_t* threads;

typedef struct {
    int pos_i;
    int qnt;
    sem_t sem;
    stats_t stats;
} thread_args_t;

sem_t sem_threads_done;

thread_args_t* g_args; 

int finalizar;

void init(int n_threads, int size) 
{
    finalizar = 0;
    sem_init(&sem_threads_done, 0, 0);
    
    threads = (pthread_t*) malloc(n_threads*sizeof(pthread_t));
    g_args = (thread_args_t*) malloc(n_threads*sizeof(thread_args_t));
    
    stats_t default_stats = {0, 0, 0, 0};
    int total_size = size * size;
    int qnt_per_thread = total_size / n_threads;
    int qnt_remainder = total_size % n_threads;

    for (int i = 0; i < n_threads; i++) {
        sem_init(&g_args[i].sem, 0, 0);
        g_args[i].stats = default_stats;
        g_args[i].pos_i = i * qnt_per_thread;
        g_args[i].qnt = qnt_per_thread;
        if (i == n_threads - 1) {
            g_args[i].qnt += qnt_remainder;
        }
        pthread_create(&threads[i], NULL, thread, (void*) &g_args[i]);
    }
    g_n_threads = n_threads;
}


void* thread(void* arg) 
{
    thread_args_t* args = (thread_args_t*) arg;

    while (1) {
        sem_wait(&args->sem);

        if (finalizar)
            pthread_exit(NULL);

        args->stats.borns = 0;
        args->stats.loneliness = 0;
        args->stats.overcrowding = 0;
        args->stats.survivals = 0;

        int pos_i = args->pos_i;
        for (int i = pos_i; i < pos_i + args->qnt; i++) {
            int cur_line = i / g_size;
            int cur_col = i - cur_line * g_size;

            int a = adjacent_to(g_board, g_size, cur_line, cur_col);

            /* if cell is alive */
            if(g_board[cur_line][cur_col]) 
            {
                /* death: loneliness */
                if (a < 2) {
                    g_newboard[cur_line][cur_col] = 0;
                    args->stats.loneliness++;
                }
                else if (a == 2 || a == 3) {
                    g_newboard[cur_line][cur_col] = g_board[cur_line][cur_col];
                    args->stats.survivals++;
                }
                else if (a > 3) {
                    /* death: overcrowding */
                    g_newboard[cur_line][cur_col] = 0;
                    args->stats.overcrowding++;
                }
            }
            else /* if cell is dead */
            {
                if(a == 3) /* new born */
                {
                    g_newboard[cur_line][cur_col] = 1;
                    args->stats.borns++;
                }
                else { 
                    /* stay unchanged */
                    g_newboard[cur_line][cur_col] = g_board[cur_line][cur_col];
                }
            }
        }
            sem_post(&sem_threads_done);
            sem_post(&sem_threads_done);
        pthread_mutex_unlock(&mtx_count);
        sem_post(&sem_threads_done);
        pthread_mutex_unlock(&mtx_count);
    }
}


void end()
{
    // Finalizar as threads
    finalizar = 1;
    for (int i = 0; i < g_n_threads; i++)
        sem_post(&g_args[i].sem);
    free(threads);
    free(g_args);
    for (int i = 0; i < g_n_threads; i++)
        sem_destroy(&g_args[i].sem);
    sem_destroy(&sem_threads_done);
}

stats_t play(cell_t **board, cell_t **newboard, int size)
{
    g_board = board;
    g_size = size;

    g_newboard = newboard;
    // Liberar as threads
    for (int i = 0; i < g_n_threads; i++)
        sem_post(&g_args[i].sem);

    // Esperar todas as threads acabarem
    for (int i = 0; i < g_n_threads; i++)
        sem_wait(&sem_threads_done);

    // Somar os stats
    stats_t stats = {0, 0, 0, 0};
    for (int i = 0; i < g_n_threads; i++) {
        stats.borns += g_args[i].stats.borns;
        stats.loneliness += g_args[i].stats.loneliness;
        stats.overcrowding += g_args[i].stats.overcrowding;
        stats.survivals += g_args[i].stats.survivals;
    }

    return stats;
    }

void print_board(cell_t **board, int size)
{
    int i, j;
    /* for each row */
    for (j = 0; j < size; j++)
    {
        /* print each column position... */
        for (i = 0; i < size; i++)
            printf("%c", board[i][j] ? 'x' : ' ');
        /* followed by a carriage return */
        printf("\n");
    }
}

void print_stats(stats_t stats)
{
    /* print final statistics */
    printf("Statistics:\n\tBorns..............: %u\n\tSurvivals..........: %u\n\tLoneliness deaths..: %u\n\tOvercrowding deaths: %u\n\n",
        stats.borns, stats.survivals, stats.loneliness, stats.overcrowding);
}

void read_file(FILE *f, cell_t **board, int size)
{
    char *s = (char *) malloc(size + 10);

    /* read the first new line (it will be ignored) */
    fgets(s, size + 10, f);

    /* read the life board */
    for (int j = 0; j < size; j++)
    {
        /* get a string */
        fgets(s, size + 10, f);
        /* copy the string to the life board */
        for (int i = 0; i < size; i++)
            board[i][j] = (s[i] == 'x');
    }

    free(s);
}