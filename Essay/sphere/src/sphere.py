import numpy
import scipy
from scipy.optimize import anneal

print anneal

def func(x):
    return numpy.sum(x*x)


sched = 'fast'
sched = 'cauchy' 
sched = 'boltzmann' 

x_guess = numpy.random.random(30)-0.5
print anneal(func, x0=x_guess, upper=1, lower=-1, schedule=sched, maxiter=40000, full_output=1)


# scipy.optimize.anneal(func, x0, args=(), schedule='fast', full_output=0, T0=None, Tf=1e-12, 
#                       maxeval=None, maxaccept=None, maxiter=401, boltzmann=1.0, learn_rate=0.5, 
#                       feps=1e-06, quench=1.0, m=1.0, n=1.0, lower=-100, upper=100, dwell=50, disp=True)


