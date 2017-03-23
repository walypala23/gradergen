from sys import argv, exit, stderr
import os
from random import randint, shuffle, seed

def run(N,H,M):

    print(N)

    short = randint(0,N)
    trees = [randint(2,H) for _ in range(N-short)] + ([1,]*short)
    shuffle(trees)

    print("".join([str(t) + " " for t in trees]))

if __name__ == "__main__":
    N, H, M, S = 5000, 35, 1000, 31

    seed(S)

    run(N,H,M)
