import numpy as np
import scipy
import numpy.polynomial.polynomial as poly


# polynomial fit with n degree
def polyfit(plt, x, y):
    x = np.array(x)
    y = np.array(y)
    coefs = poly.polyfit(x, y, 2)
    ffit = poly.polyval(x, coefs)
    plt.plot(x, ffit)


def exponential_fit(x, a, b, c):
    return a*np.exp(-b*x) + c

def exp_fit(x, y):
    return scipy.optimize.curve_fit(exponential_fit, x, y)





