void cerca(int N, char** mat, int &A, int &B, int &C) {
    for (int i=0; i<N; i++)
        for (int j=0; j<N; j++) {
            mat[i][j] -= '0';
        }
    for (int i=0; i<N; i++)
        for (int j=i+1; j<N; j++)
            for (int k=j+1; k<N; k++) {
                bool cor = mat[i][j] && mat[j][k] && mat[k][i];
                cor |= mat[i][k] && mat[k][j] && mat[j][i];
                if (cor) {
                    A = i+1;
                    B = j+1;
                    C = k+1;
                    return;
                }
            }
    A = B = C = -1;
}
