import os
import csv
import numpy as np


def format_plot(plt, title, ax, fontsize):
   # plt.rc('text', usetex=True)
   # plt.rc('font', family='serif')
   # plt.rc('text.latex', preamble=r'\usepackage{textgreek}')
    ax.set_title(title, fontsize=fontsize)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def scalar_formatter(ax):
    from matplotlib.ticker import ScalarFormatter
    ax.xaxis.set_major_formatter(ScalarFormatter())
