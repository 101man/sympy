from sympy import Lambda, Symbol, Function, WildFunction, Derivative, sqrt, \
        log, exp, Rational, Real, sign, Basic, sin, cos, diff, I, re, im, \
        oo, zoo, nan, E, expand
from sympy.utilities.pytest import XFAIL
from sympy.utilities.test import REPR0
from sympy.abc import x, y


def test_log():
    assert log(2) > 0
    assert log(1).is_zero
    assert log(0.5).is_negative == True

def test_exp_log():
    x = Symbol("x", real=True)
    assert log(exp(x)) == x
    assert exp(log(x)) == x

def test_log_expansion():
    x = Symbol("x", real=True)
    y = Symbol("y", real=True)

    # ok in interactive, fails in py.test
    #assert log(x*y) != log(x)+log(y)
    #assert log(x**2) != 2*log(x)

    assert log(x*y).expand() == log(x)+log(y)
    assert log(x**2).expand() == 2*log(x)
    assert (log(x**-5)**-1).expand() == -1/log(x)/5

def test_log_hashing_bug():
    x = Symbol("y")
    assert x != log(log(x))
    assert hash(x) != hash(log(log(x)))
    assert log(x) != log(log(log(x)))

    e = 1/log(log(x)+log(log(x)))
    assert e.base.func is log
    e = 1/log(log(x)+log(log(log(x))))
    assert e.base.func is log

    x = Symbol("x")
    e = log(log(x))
    assert e.func is log
    assert not x.func is log
    assert hash(log(log(x))) != hash(x)
    assert e != x

def test_sign():
    assert sign(log(2)) == 1

def test_exp_bug():
    x = Symbol("x")
    assert exp(1*log(x)) == x

def test_exp_expand():
    x = Symbol("x")
    y = Symbol("y")

    e = exp(log(Rational(2))*(1+x)-log(Rational(2))*x)
    assert e.expand() == 2
    # XXX The RHS is automatically combined so that it equals the LHS
    #assert exp(x+y) != exp(x)*exp(y)
    assert exp(x+y).expand() == exp(x)*exp(y)


def test_f_expand_complex():
    f = Function('f')
    x = Symbol('x', real=True)
    z = Symbol('z')

    assert f(x).expand(complex=True)        == I*im(f(x)) + re(f(x))
    assert exp(x).expand(complex=True)      == exp(x)
    assert exp(I*x).expand(complex=True)    == cos(x) + I*sin(x)
    assert exp(z).expand(complex=True)      == cos(im(z))*exp(re(z)) + \
                                             I*sin(im(z))*exp(re(z))

def test_bug1():
    x = Symbol("x")
    w = Symbol("w")

    e = sqrt(-log(w))
    assert e.subs(log(w),-x) == sqrt(x)

    e = sqrt(-5*log(w))
    assert e.subs(log(w),-x) == sqrt(5*x)

def test_general_function():
    nu = Function('nu', nargs=1)
    x = Symbol("x")
    y = Symbol("y")

    e = nu(x)
    edx = e.diff(x)
    edy = e.diff(y)
    edxdx = e.diff(x).diff(x)
    edxdy = e.diff(x).diff(y)
    assert e == nu(x)
    assert edx != nu(x)
    assert edx == diff(nu(x), x)
    assert edy == 0
    assert edxdx == diff(diff(nu(x), x), x)
    assert edxdy == 0

def test_derivative_subs_bug():
    x = Symbol("x")
    l = Function('l', nargs=1)
    n = Function('n', nargs=1)

    e = diff(n(x), x)
    assert e.subs(n(x), l(x)) != e
    assert e.subs(n(x), l(x)) == diff(l(x), x)
    assert e.subs(n(x), -l(x)) == diff(-l(x), x)

def test_derivative_linearity():
    x = Symbol("x")
    y = Symbol("y")
    n = Function('n', nargs=1)

    assert diff(-n(x), x) == -diff(n(x), x)
    assert diff(8*n(x), x) == 8*diff(n(x), x)
    assert diff(8*n(x), x) != 7*diff(n(x), x)
    assert diff(8*n(x)*x, x) == 8*n(x) + 8*x*diff(n(x), x)
    assert diff(8*n(x)*y*x, x) == 8*y*n(x) + 8*y*x*diff(n(x), x)

def test_derivative_evaluate():
    x = Symbol('x')

    assert Derivative(sin(x), x) != diff(sin(x), x)
    assert Derivative(sin(x), x).doit() == diff(sin(x), x)

@XFAIL
def test_combine():
    # XXX combine no longer exists
    x = Symbol("x")
    y = Symbol("y")
    assert exp(x)*exp(-x) != 1
    assert (exp(x)*exp(-x)).combine() == 1

    assert exp(x)**2 != exp(2*x)
    assert (exp(x)**2).combine() == exp(2*x)

    assert exp(x)*exp(-x/2)*exp(-x/2) != 1
    assert (exp(x)*exp(-x/2)*exp(-x/2)).combine() == 1

    assert (2*log(x)).combine() == log(x**2)
    assert exp(2*log(x)) != x**2
    assert exp(2*log(x)).combine() == x**2

    assert exp(x)*exp(-x)-1 !=0
    assert (exp(x)*exp(-x)-1).combine() == 0

    assert (2*exp(x)*exp(-x)).combine() == 2
    assert (x/exp(x)*exp(-x)).combine() == x*exp(-2*x)


@REPR0
def test_function_str():
    x = Symbol('x')
    f = Function('f')
    fx= f(x)
    w = WildFunction('w')

    # XXX we are not using repr(...) str(...) here, becuase Basic.__repr__ and __str__
    #     are doing some tricks, and repr(...) is not always a repr.
    assert repr(fx) == "Function('f')(Symbol('x'))"
    assert repr(w)  == "WildFunction('w')"

    assert str(fx)  == "f(x)"
    assert str(w)   == "w_"


@XFAIL
@REPR0
def test_unapplied_function_str():
    f = Function('f')

    assert repr(f)     == "Function('f')"   # this does not work
    assert str(f)      == "f"               # this does not work

def test_Lambda():
    e = Lambda(x, x**2)
    f = Function('f')
    assert e(4) == 16
    assert e(x) == x**2
    assert e(y) == y**2
    
    assert Lambda(x, x**2) == Lambda(x, x**2)
    assert Lambda(x, x**2) == Lambda(y, y**2)
    assert Lambda(x, x**2) != Lambda(y, y**2+1)
    assert Lambda(x,y,x**y) == Lambda(y,x,y**x)
    assert Lambda(x,y,x**y) != Lambda(x,y,y**x)
    
    assert Lambda(x,y,x**y)(x,y) == x**y 
    assert Lambda(x,y,x**y)(x) == Lambda(y,x**y)
    assert Lambda(x,y,x**y)(x)(y) == x**y 
    assert Lambda(x,y,x**y)(x)(3) == x**3
    assert Lambda(x,y,x**y)(3)(y) == 3**y
    assert Lambda(x,y,x**y)(3)(3) == 3**3
    assert Lambda(x,y,x**y)(3,3) == 3**3
    assert Lambda(x,y,x**y)(x,3) == x**3
    assert Lambda(x,y,x**y)(3,y) == 3**y
    assert Lambda(x,f(x))(x) == f(x)
    assert Lambda(x,f(x))() == Lambda(x,f(x))
    assert Lambda(x,x**2)(e(x)) == x**4
    assert e(e(x)) == x**4
    assert Lambda(x,y,f(x)+f(y))(x) == Lambda(y,f(x)+f(y))
    #doesn't work yet:
    #class F(Function):
    #    pass
    #assert Lambda(x, F(x)) == F

def test_expand_function():
    assert expand(x+y) == x + y
    assert expand(x+y, complex=True) == I*im(x) + I*im(y) + re(x) + re(y)


def test_function_comparable():
    x = Symbol('x')

    assert sin(x).is_comparable == False
    assert cos(x).is_comparable == False

    assert sin(Real('0.1')).is_comparable   == True
    assert cos(Real('0.1')).is_comparable   == True

    assert sin(E).is_comparable     == True
    assert cos(E).is_comparable     == True

    assert sin(Rational(1,3)).is_comparable == True
    assert cos(Rational(1,3)).is_comparable == True

@XFAIL
def test_function_comparable_fail():
    x = Symbol('x')

    assert sin(oo).is_comparable    == False
    assert sin(-oo).is_comparable   == False
    assert sin(zoo).is_comparable   == False
    assert sin(nan).is_comparable   == False

