#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

static FILE *fr, *fw;

// Declaring variables
static int N;
static int M;
static int S;
static int* P;
static int* from;
static int* to;
static int* length;
static int H;
static int W;
static char** R;
static char** G;
static char** B;
static int res;
static int* scelti;
static double* colore;

// Declaring functions
void contapersone(int M, int* from, int* to);
void sceglicolori(int res, int* scelti, double* colore);

int main() {
	#ifdef EVAL
		fr = fopen("input.txt", "r");
		fw = fopen("output.txt", "w");
	#else
		fr = stdin;
		fw = stdout;
	#endif

	// Reading input
	fscanf(fr, "%d %d %d", &N, &M, &S);
	P = (int*)malloc(N * sizeof(int));
	for (int i0 = 0; i0 < N; i0++) {
		fscanf(fr, "%d", &P[i0]);
	}
	from = (int*)malloc(M * sizeof(int));
	to = (int*)malloc(M * sizeof(int));
	length = (int*)malloc(M * sizeof(int));
	for (int i0 = 0; i0 < M; i0++) {
		fscanf(fr, "%d %d %d", &from[i0], &to[i0], &length[i0]);
	}
	fscanf(fr, "%d %d", &H, &W);
	R = (char**)malloc(H * sizeof(char*));
	for (int i0 = 0; i0 < H; i0++) {
		R[i0] = (char*)malloc(W * sizeof(char));
	}
	G = (char**)malloc(H * sizeof(char*));
	for (int i0 = 0; i0 < H; i0++) {
		G[i0] = (char*)malloc(W * sizeof(char));
	}
	B = (char**)malloc(H * sizeof(char*));
	for (int i0 = 0; i0 < H; i0++) {
		B[i0] = (char*)malloc(W * sizeof(char));
	}
	for (int i0 = 0; i0 < H; i0++) {
		for (int i1 = 0; i1 < W; i1++) {
			fscanf(fr, "%c %c %c", &R[i0][i1], &G[i0][i1], &B[i0][i1]);
		}
	}

	// Calling functions
	contapersone(M, from, to);
	sceglicolori(res, scelti, colore);

	// Writing output
	fprintf(fw, "%d\n", res);
	for (int i0 = 0; i0 < res; i0++) {
		fprintf(fw, "%d %lf\n", scelti[i0], colore[i0]);
	}
	fprintf(fw, "\n");
	
	fclose(fr);
	fclose(fw);
	return 0;
}
