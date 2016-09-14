# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***
int N

# M non esiste e dovrebbe dare errore
int A[M]
int res

***prototypes***
int f(int N)

***input***
N
A[N]

***calls***
res = f(N)

***output***
res
