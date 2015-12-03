long long int S;

void inizializza(long long int s) {
	S = s;
}

void aggiungi(int N, long long int* X) {
	for (int i = 0; i < N; i++) S += X[i];
}

long long int risultato() {
	return S;
}

