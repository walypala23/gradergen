#include <cstdio>
#include <cstdlib>

int n = 10000;

int main() {
    printf("%d\n", n);
    for (int i=0; i<n; i++) {
        for (int j=0; j<n; j++) {
            putchar_unlocked('0' + rand() % 2);
        }
        putchar_unlocked('\n');
    }
}
