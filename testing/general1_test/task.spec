# Le righe che iniziano con # sono commenti.
# La stringa ***sezione*** indica l'inizio di una nuova sezione.
# Le sezioni devono essere sempre presenti tutte, l'ordine non conta ma è
# meglio se sono nell'ordine: variables, functions, input, output


***variables***

int N
int M
int S
int P[N]
int from[M]
int too[M]
int length[M]

int H
int W
char R[H][W]
char G[H][W]
char B[H][W]


int res
int scelti[res]
real colore[res]

***prototypes***
int contapersone(int M, int da[], int a[])

sceglicolori(int dim, int[] &scelti, real[] &colori)

***input***

N M S
P[]
from[] too[] length[]

H W
R[][] G[][] B[][]



***calls***
res = contapersone(M, from, too)

sceglicolori(res, scelti, colore)

***output***

res
scelti[] colore[]
R[][]
