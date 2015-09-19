from sys import argv, exit, stderr
import os
from random import choice, sample, shuffle, seed as rseed
try:
    from numpy.random import randint, seed as nseed
except:
    nseed = rseed
    from random import randint as _r
    def randint(A, B):
        return _r(A, B-1)

def run(N,H,M):

    print N

    short = randint(0,N+1)
    trees = [randint(2,H+1) for _ in xrange(N-short)] + ([1,]*short)
    shuffle(trees)

    for i in trees:
        print i,

if __name__ == "__main__":
    N, H, M, S = 5000, 35, 1000, 31

    nseed(S)
    rseed(S)

    run(N,H,M)
