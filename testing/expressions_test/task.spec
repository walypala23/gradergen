# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***
int N
int A[3*N-5]
int B[3*N-5]
int C[3*N-5]

***prototypes***
moltiplica(int N, int[] X, int[] Y, int[] &res)

***input***
N
A[] B[]

***calls***
moltiplica(N, A, B, C)

***output***
C[]
