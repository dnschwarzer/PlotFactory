import os
import csv
import numpy as np


def format_plot(plt, title, ax, fontsize):
    ax.set_title(title, fontname='Ubuntu', fontsize=fontsize)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Ubuntu Mono'
    plt.rcParams['axes.labelweight'] = 'bold'
    import matplotlib.pylab as pylab
    params = {'legend.fontsize': 'x-large',
             'axes.labelsize': 'x-large',
             'axes.titlesize': 'x-large',
             'xtick.labelsize': '20',
             'ytick.labelsize': '20'}
    pylab.rcParams.update(params)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def scalar_formatter(ax):
    from matplotlib.ticker import ScalarFormatter
    ax.xaxis.set_major_formatter(ScalarFormatter())
