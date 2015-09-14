#include <stdlib.h>

int contapersone(int M, int* from, int* too) {
	int xxx = from[M-2] + from[M-1] + too[1];
	if (xxx > 10000) return 10000;
	return xxx;
}

void sceglicolori(int res, int* scelti, double* colore) {
	int i;
	
	for (i = 0; i < res ; i++) {
		scelti[i] = i;
		colore[i] = 23.0;
	}
}

