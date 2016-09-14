# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***
int N
longint S
longint X[N]
longint res

***prototypes***
inizializza(longint first)
aggiungi(longint X)
longint risultato()
AggiungiTutti(int N, longint X[]) {grader}

***input***
N
S
X[]

***calls***
inizializza(S)
AggiungiTutti(N, X)
res = risultato()

***output***
res
