# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***
int N
int A[N]
int B[N]


***prototypes***
int moltiplica(int x, int y)

***calls***
repeat N: B[i0] = moltiplica(A[i0], i0)

***input***
N
A[]

***output***
B[]
