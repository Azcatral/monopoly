''' use deque instead of list in apply_funcs to increase performance when doing insert(0, ...) '''
from .monopoly import *
def validate(expr):
    count = 0
    for tok in expr:
        count += (tok == '(')
        count -= (tok == ')')
        if count < 0:
            return False
    return count == 0

def apply_funcs(_lst):
    # pop(i) and insert(i) in lists are worse in performance than pop() and append()
    if len(_lst) == 1:
        return _lst[0]
    
    lst = _lst[:]
    add = lambda a, b: a+b
    sub = lambda a, b: a-b
    mul = lambda a, b: a*b
    exp = lambda a, b: a**b
    func = {'add': add, 'sub': sub, 'mul': mul, 'exp': exp}

    # multiplication precedence; deal with them first
    while 'mul' in lst:
        i = lst.index('mul')
        second, operator, first = lst.pop(i+1), lst.pop(i), lst.pop(i-1)
        lst.insert(i-1, func[operator](first, second))

    
    while len(lst) > 1:
        first, operator, second = lst.pop(0), lst.pop(0), lst.pop(0)
        lst.insert(0, func[operator](first, second)) # don't use lst[-1] = ... if you don't want to replace. use lst.append instead!

    return lst[0]

# the depth variable is key here! remember this idea
def evaluate(expr, debug=False): # parses and calculates an expression in-place
    if not validate(expr):
        raise ValueError('there\'s something wrong with the parentheses')
    expr = list(match.group() for match in regex.finditer(r'(?(?=(?<mono>[\da-zA-Z\*\^\/]+))\g<mono>|.)', expr))
    ismono = lambda s: s not in '(+-)' and not s.startswith('**')
    ops = []
    innerops = ops
    depth = 0
    for i, tok in enumerate(expr):
        if debug:
            for var, value in locals().items():
                print(f'{var}: {value}')
            print('='*50)
        n = len(expr)
        before = expr[i-1 if i>=1 else 0]
        after = expr[i+1 if i<n-1 else n-1]
        if tok == '(':
            depth += 1
            if ismono(before):
                innerops.append('mul')
            prev_innerops = innerops
            innerops = []
            prev_innerops.append(innerops)
        elif tok == '+':
            innerops.append('add')
        elif tok == '-':
            innerops.append('sub')
        elif tok == '*':
            innerops.append('mul')
        elif tok.startswith('**'):
            innerops.append('exp')
            innerops.append(int(tok[2:]))
        elif tok == ')':
            depth -= 1
            prev_innerops.pop()
            prev_innerops.append(apply_funcs(innerops))
            innerops = prev_innerops
            prev_innerops = ops
            for i in range(depth-1):
                prev_innerops = prev_innerops[-1]
            if ismono(after) or after == '(':
                innerops.append('mul')
        elif tok == ' ':
            continue
        else:
            innerops.append(Poly(tok))
    return apply_funcs(ops)

""" def parse(expr): # parse expression (currently doesn't work)
    if not validate(expr):
        raise ValueError('There\'s something wrong with the parentheses')
    expr = list(match.group() for match in regex.finditer(r'(?(?=(?<mono>[\da-zA-Z\*\^]+))\g<mono>|.)', expr))
    ismono = lambda s: s not in '(+-)'
    ops = []
    innerops = ops
    depth = 0
    for i, tok in enumerate(expr):
        n = len(expr)
        before = expr[i-1 if i>=1 else 0]
        after = expr[i+1 if i<n-1 else n-1]
        if tok == '(':
            depth += 1
            if ismono(before):
                innerops.append('mul')
            prev_innerops = innerops
            innerops = []
            prev_innerops.append(innerops)
        elif tok == '+':
            innerops.append('add')
        elif tok == '-':
            innerops.append('sub')
        elif tok == '*':
            innerops.append('mul')
        elif tok == ')':
            depth -= 1
            prev_innerops.pop()
            innerops = prev_innerops
            prev_innerops = ops
            for i in range(depth-1):
                prev_innerops = prev_innerops[-1]
            if ismono(after) or after == '(':
                innerops.append('mul')
        elif tok == ' ':
            continue
        else:
            innerops.append(tok)
    return ops """

if __name__ == "__main__":
    print(evaluate("(1/2n(n+1)(2n+1))**3"))
    
