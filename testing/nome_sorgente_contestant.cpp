#include <cstdlib>
#include <algorithm>


int contapersone(int M, int* from, int* too) {
	return std::min(10000, from[M/2] + from[M-1] + too[1]);
}

void sceglicolori(int res, int* scelti, double* colore) {
	int i;
	
	scelti = (int*)malloc(res * sizeof(int));
	colore = (double*)malloc(res * sizeof(double));
	for (i = 0; i < res ; i++) {
		scelti[i] = i;
		colore[i] = 23.0;
	}
}

