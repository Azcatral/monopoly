# TODO: - give constant numerals an exponent of 0 because it makes more sense and also fixes erroneous sorting-by-exponent in Poly
#       - validate input in Fraction, Mono, Poly
import regex

class Fraction:
    ''' class for fractions to be used as monomial coefficients
        --- usage: Fraction("numerator/denominator") '''
    def __init__(self, expr='0'):
        from math import gcd

        self.expr = expr
        self.sign = ['+', '-'][expr.startswith('-')]
        if self.sign == '-':
            if len(expr) == 1: # Mono('-x') => Fraction('-') => -1
                expr += '1'
            self.__dict__ = (-Fraction(expr[1:])).__dict__ # gruesome way to assign Fraction to (negative) Fraction, but hey it works!
            self.sign = '-'
        else:
            if expr.startswith('+'):
                if len(expr) == 1:
                    expr = '1'
                else:
                    expr = expr[1:]
            
            if '/' not in expr:
                expr += '/1'

            self.numerator, self.denominator = map(int, regex.findall(r'(\d+)/(\d+)', expr)[0])

            g = gcd(self.numerator, self.denominator)
            self.numerator //= g; self.denominator //= g

            self.val = self.numerator / self.denominator
            self.parts = self.numerator, self.denominator
    
    def __neg__(self):
        neg = Fraction(self.expr)
        neg.expr = '-' + neg.expr
        neg.numerator = -self.numerator
        neg.val = -self.val
        neg.parts = self.numerator, self.denominator
        return neg
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.parts == other.parts
    
    def __add__(self, other):
        numerator = self.numerator*other.denominator + other.numerator*self.denominator
        denominator = self.denominator * other.denominator
        return Fraction(f'{numerator}/{denominator}')

    def __sub__(self, other):
        return self + (-other)
    
    def __mul__(self, other):
        numerator = self.numerator * other.numerator
        denominator = self.denominator * other.denominator
        return Fraction(f'{numerator}/{denominator}')
    
    def __bool__(self):
        return self.val != 0

    def __repr__(self):
        return f'Fraction({self.numerator}{f"/{self.denominator}" if self.denominator != 1 else ""})'
    
    def __str__(self):
        return f'{self.numerator}{f"/{self.denominator}" if self.denominator != 1 else ""}'

Fraction.zero = Fraction()
Fraction.one = Fraction('1')
################################################################################################################################################################################
class Mono:
    ''' class for monomials and their arithmetic (does not validate input)
        --- usage: Mono("{coeff}{var}^{exp}") or Mono("{coeff}*{var}**{exp}), e.g. Mono("n"), Mono("9*x"), Mono("4y^2"), Mono("z**3"), also: Mono("10*a^3"), Mono("2/3i**7") and Mono("23/9") '''
        self.coeff, self.var, self.exp = regex.findall(r'((?:\+|-)?(?:\d+)?(?:\/\d+)?)?\*?([a-zA-Z])?(?:(?:\*\*|\^)(\d*))?', expr)[0]
        
        if not self.coeff:
            self.coeff = '1'
        if not self.exp:
            self.exp = 1
            
        self.coeff, self.exp = Fraction(self.coeff), int(self.exp)
        if self.exp == 0 or self.coeff == Fraction.zero: 
            self.var = ''
            self.exp = 1
        self.parts = self.coeff, self.var, self.exp

    def beautify(self):
        coeff, var, exp = self.coeff, self.var, self.exp
        if not self.coeff:
            var = ''
        elif self.coeff.val == 1:
            if self.var:
                coeff = ''
            else:
                coeff = '1'
        elif self.coeff.val == -1:
            if self.var:
                coeff = '-'
            else:
                coeff = '-1'
        
        if self.exp == 1:
            exp = ''
        
        return str(coeff), var, exp

    def __neg__(self):
        return Mono(f'{-self.coeff}*{self.var}**{self.exp}')

    def __add__(self, other):
        if (self.var != other.var):
            raise ValueError(f"cannot add two monomials of different variables: \"{self.var}\" and \"{other.var}\"")
        elif (self.exp != other.exp):
            return Poly(self.expr) + Poly(other.expr)
        else:
            coeff = self.coeff + other.coeff
            var = self.var
            exp = self.exp
            return Mono(f'{coeff}*{var}**{exp}')
    
    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if not self.var:
            if not other.var:
                return Mono(f'{self.coeff*other.coeff}')
            return other*self
        if not other.var:
            return Mono(f'{self.coeff*other.coeff}*{self.var}**{self.exp}')
        if (self.var == other.var):
            coeff = self.coeff * other.coeff
            var = self.var
            exp = self.exp + other.exp
            return Mono(f'{coeff}*{var}**{exp}')
        else:
            raise ValueError(f"cannot multiply two monomials of different variables: \"{self.var}\" and \"{other.var}\"")
    
    def __pow__(self, n): # n is a non-negative number
        if (n == 0):
            return Mono('1')
        else:
            res = self
            for i in range(n-1):
                res = res * self
            return res

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.parts == other.parts
    
    def __repr__(self):
        coeff, var, exp = self.beautify()
        caret = '^' if exp else ''
        return f'Mono({coeff}{var}{caret}{exp})'

    def __altrepr__(self):
        coeff, var, exp = self.beautify()
        caret = '^' if exp else ''
        coeff = coeff[coeff.startswith('-'):]
        return f'{self.coeff.sign} {coeff}{var}{caret}{exp}'
    
    def __str__(self):
        coeff, var, exp = self.beautify()
        times = '*' if coeff.isdigit() and var else ''
        asterisks = '**' if exp else ''
        return f'{coeff}{times}{var}{asterisks}{exp}'  

    def __altstr__(self):
        coeff, var, exp = self.beautify()
        times = '*' if any(c.isdigit() for c in coeff) and var else ''
        asterisks = '**' if exp else ''
        coeff = coeff[coeff.startswith('-'):]
        return f'{self.coeff.sign} {coeff}{times}{var}{asterisks}{exp}'        
################################################################################################################################################################################
class Poly:
    ''' class for a polynomial of Monos '''
    def __init__(self, expr):
        self.expr = expr
        monos = sorted((Mono(match) for match in regex.sub(r'\s?(\+|-)\s?', r' \1', expr).split()), key=lambda m: m.exp + bool(m.var), reverse=True)
        # self.monos = sorted(map(Mono, regex.split(r'\s?\+\s?', expr)), key=lambda m: m.exp, reverse=True)
        
        self._dict = dict()
        for mono in monos:
            varexp = f'{mono.var}^{mono.exp}'
            try:
                self._dict[varexp] += mono.coeff
                if self._dict[varexp].val == 0:
                    self._dict.pop(varexp)
            except KeyError:
                self._dict[varexp] = mono.coeff
        self.neg = '-' if self._dict[tuple(self._dict.keys())[0]].sign == '-' else '' # not worth setting up an OrderedDict... temporary ugly fix
        expr = self.neg + ' '.join(Mono(f'{self._dict[varexp]}{varexp}').__altrepr__() for varexp in self._dict.keys())[2:]
        self.monos = list((Mono(match) for match in regex.sub(r'\s?(\+|-)\s?', r' \1', expr).split()))
        
        self.var = self.monos[0].var
        self.deg = self.monos[0].exp

    def __neg__(self):
        expr = self.expr.replace('-', 's').replace('+', '-').replace('s', '+')
        neg = self.expr.startswith('-')
        if not neg:
            expr = '- ' + expr
        return Poly(expr)
    
    def __add__(self, other):
        return Poly(f'{self.expr} {str(other)}') # be careful! Mono's expr can be used here
    
    def __sub__(self, other):
        return self + (-other)
    
    def __mul__(self, other):
        res = ''
        for s_mono in self.monos:
            for o_mono in other.monos:
                res += (s_mono*o_mono).__altstr__()
        neg = '-' if res.startswith('-') else ''
        return Poly(neg + res[2:])
    
    def __pow__(self, n): # n is a non-negative number
        if (n == 0):
            return Poly('1')
        else:
            res = self
            for i in range(n-1):
                res = res * self
            return res

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.monos == other.monos

    def __repr__(self):
        return f'Poly({self.neg}{" ".join(map(lambda m: m.__altrepr__(), self.monos))[2:]})'

    def __str__(self):
        return f'{" ".join(map(lambda m: m.__altstr__(), self.monos))}'

    def __call__(self, arg):
        func = eval(f'lambda {self.var}: {self}')
        return func(arg)

    def prettyprint(self):
    	
        def prettyexp(power):
            powers = [8304, 185, 178, 179, 8308, 8309, 8310, 8311, 8312, 8313]
            res = ''
            for char in str(power):
                res += chr(powers[int(char)])
            return res

        def monoprint(mono):
            coeff, var, exp = mono.beautify()
            exp = prettyexp(mono.exp) if var else '' # numbers have a default exp of 1
            neg = coeff.startswith('-')
            coeff = coeff[neg:]
            sign = ['+', '-'][neg]

            return f'{sign} {coeff}{var}{exp}'
        
        return ' '.join(map(monoprint, self.monos))[2:]


if __name__ == "__main__":
    print(f'(x+1)^5 = {repr(Poly("x+1")**5})')
