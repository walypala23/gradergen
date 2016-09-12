# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***
int N
char mat[N][N]

int A
int B
int C


***prototypes***
cerca(int N, char[][] mat, int &A, int &B, int &C)

***calls***
cerca(N, mat, A, B, C)


***input***
N
mat[][]


***output***
A B C
