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
static int* too;
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
void contapersone(int M, int* from, int* too);
void sceglicolori(int res, int* scelti, double* colore);

// Begin fast input library

static inline char fast_read_char() {
	char c = fgetc_unlocked(fr);
	// ignore whitespaces
	while (	c == 0x20 || c == 0x09 || c == 0x0a 
			|| c == 0x0b || c == 0x0c || c == 0x0d) c = fgetc_unlocked(fr);
	return c;
}

static inline int fast_read_int() { // speed x5
	short int minus = 0;
	int res = 0;
	char c = fgetc_unlocked(fr);
	while (c != '-' && (c < '0' || '9' < c)) c = fgetc_unlocked(fr);

	if (c == '-') minus = 1, c = fgetc_unlocked(fr);
	
	do{
		res = res * 10 + (c - '0');
		c = fgetc_unlocked(fr);
	}
	while ('0' <= c && c <= '9');
	
	if (minus) return -res;
	else return res;
}

static inline long long int fast_read_longint() {
	short int minus = 0;
	long long int res = 0;
	char c = fgetc_unlocked(fr);
	while (c != '-' && (c < '0' || '9' < c)) c = fgetc_unlocked(fr);

	if (c == '-') minus = 1, c = fgetc_unlocked(fr);
	
	do{
		res = res * 10ll + (long long int)(c - '0');
		c = fgetc_unlocked(fr);
	}
	while ('0' <= c && c <= '9');
	
	if (minus) return -res;
	else return res;
}

static inline double fast_read_real() { //TODO
	double x;
	fscanf(fr, "%lf", &x);
	return x;
}

static inline void fast_write_char(char c) {
	fputc_unlocked(c, fw);
}

static inline void fast_write_int(int x) { // speed x2
	static short int digits[16];
	if (x == 0) {
		fputc_unlocked('0', fw);
		return;
	}
	if (x < 0) {
		fputc_unlocked('-', fw);
		x = -x;
	}
	short int i = -1;
	while (x) {
		i++;
		digits[i] = x%10; 
		x /= 10;
	}
	for (; i >= 0; i--) fputc_unlocked('0' + digits[i], fw);
}

static inline void fast_write_longint(long long int x) { // speed x2
	static short int digits[32];
	if (x == 0) {
		fputc_unlocked('0', fw);
		return;
	}
	if (x < 0) {
		fputc_unlocked('-', fw);
		x = -x;
	}
	short int i = -1;
	while (x) {
		i++;
		digits[i] = x%(10ll); 
		x /= 10ll;
	}
	for (; i >= 0; i--) fputc_unlocked('0' + digits[i], fw);
}

static inline void fast_write_real(double x) { //TODO
	fprintf(fw, "%lf", x);
}

// End fast input library

int main() {
	#ifdef EVAL
		fr = fopen("input.txt", "r");
		fw = fopen("output.txt", "w");
	#else
		fr = stdin;
		fw = stdout;
	#endif

	// Iterators used in for loops
	int i0, i1;

	// Reading input
	N = fast_read_int();
	M = fast_read_int();
	S = fast_read_int();
	P = (int*)malloc(N * sizeof(int));
	for (i0 = 0; i0 < N; i0++) {
		P[i0] = fast_read_int();
	}
	from = (int*)malloc(M * sizeof(int));
	too = (int*)malloc(M * sizeof(int));
	length = (int*)malloc(M * sizeof(int));
	for (i0 = 0; i0 < M; i0++) {
		from[i0] = fast_read_int();
		too[i0] = fast_read_int();
		length[i0] = fast_read_int();
	}
	H = fast_read_int();
	W = fast_read_int();
	R = (char**)malloc(H * sizeof(char*));
	for (i0 = 0; i0 < H; i0++) {
		R[i0] = (char*)malloc(W * sizeof(char));
	}
	G = (char**)malloc(H * sizeof(char*));
	for (i0 = 0; i0 < H; i0++) {
		G[i0] = (char*)malloc(W * sizeof(char));
	}
	B = (char**)malloc(H * sizeof(char*));
	for (i0 = 0; i0 < H; i0++) {
		B[i0] = (char*)malloc(W * sizeof(char));
	}
	for (i0 = 0; i0 < H; i0++) {
		for (i1 = 0; i1 < W; i1++) {
			R[i0][i1] = fast_read_char();
			G[i0][i1] = fast_read_char();
			B[i0][i1] = fast_read_char();
		}
	}

	// Calling functions
	contapersone(M, from, too);
	sceglicolori(res, scelti, colore);

	// Writing output
	fast_write_int(res);
	fast_write_char(' ');
	fast_write_char('\n');
	for (i0 = 0; i0 < res; i0++) {
		fast_write_int(scelti[i0]);
		fast_write_char(' ');
		fast_write_real(colore[i0]);
		fast_write_char(' ');
		fast_write_char('\n');
	}
	for (i0 = 0; i0 < H; i0++) {
		for (i1 = 0; i1 < W; i1++) {
			fast_write_char(R[i0][i1]);
			fast_write_char(' ');
		}
		fast_write_char('\n');
	}
	
	fclose(fr);
	fclose(fw);
	return 0;
}
