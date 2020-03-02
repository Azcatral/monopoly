from .evaluate import *
from .monopolywithdecimal import *
from functools import reduce

def pascal(n):
    p = n
    for i in range(2, n//2+1):
        p *= (n-i+1)
        p //= i
        yield p

binom = lambda n: (lambda l: l[:-1] + l[-1:]*(n%2) + l[::-1] + [n, 1])([*pascal(n)])
add = lambda itr: reduce(lambda x, y: x+y, itr)


ans = [Poly('n+1'), evaluate('1/2n(n+1)'), evaluate('1/6n(n+1)(2n+1)'), evaluate('(1/2n(n+1))**2')]
def solve(k):
    if k >= len(ans):
        coeffs = map(Poly, map(str, binom(k+1)))
        formers = (solve(k-i) for i in range(1, k+1))
        addends = map(lambda x, y: x*y, coeffs, formers)
        ans.append(Poly(f'1/{k+1}')*(Poly('n+1')**(k+1)-add(addends)))
    return ans[k]

sumpowers = lambda k, n: sum(Decimal(i)**k for i in range(1, n+1))
def check(k, until=100):
    flag = True
    for i in range(1, until+1):
        if (diff := (slv := round(solve(k)(Decimal(i)))) - (smpwr := sumpowers(k, i))) != 0:
            flag = False
            print(f'k: {k}, i: {i}, solve: {slv}, sumpowers: {smpwr}, diff: {diff}')
    if flag:
        return "everything worked correctly! Hooray!!!"
    else:
        return "Oops. Better luck next time!"
