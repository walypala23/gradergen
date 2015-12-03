void Abbatti(int, int);

void Pianifica(int N, int H[]) {
	for (int i=0; i<N/2; i++) {
		if (H[i] > 10) {
			Abbatti(i, 0);
		} else {
			Abbatti(N - i, 1);
		}
	}
}
