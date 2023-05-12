import os
import csv
import numpy as np
import matplotlib.ticker as ticker


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


def custom_formatter(x, pos):
    decimal_places = abs(int(np.floor(np.log10(abs(x))))) if abs(x) > 0 else 0
    format_string = "{:." + str(decimal_places) + "f}"
    formatted = format_string.format(x)
    # remove trailing zeros and decimal point if not necessary
    formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    return formatted


def scalar_formatter(ax):
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(custom_formatter))

