import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import pdf_creator as pdfc
import led_properties
import LedList as ll
from numpy.polynomial import Polynomial
import math
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class AuswertungExtensionMulti():

    color_wheel = ["black", "blue", "red", "green", "yellow", "cyan", "magenta", "black", "black", "black", "black"]

    def __init__(self, filepath, limit_den_be, limit_den_end, limit_vol_beg, limit_vol_end, summary):
        self.filepath = filepath
        self.limit_x_axis_density_begin = limit_den_be
        self.limit_x_axis_density_end = limit_den_end
        self.limit_x_axis_voltage_begin = limit_vol_beg
        self.limit_x_axis_voltage_end = limit_vol_end
        self.summary_plot_paths = summary
        self.fontsize = 35

    def find_min_op(self, led_lists):
        op_idx_li = []
        for led_list in led_lists:
            op_idx = 0
            while led_list.current_density_array_mean[op_idx] == 0:
                op_idx = op_idx + 1
            op_idx_li.append(led_list.current_density_array_mean[op_idx + 1])

        return min(op_idx_li)

    async def plot_save_c_avg(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title, fontsize=self.fontsize)
        plt.xlim([self.find_min_op(led_lists), self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)
        color_cnt = 0

        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            ax.plot(led_list.current_density_array_mean, led_list.op_power_array_mean, self.color_wheel[color_cnt], label = label)
            color_cnt = color_cnt + 1

        plt.legend()

        # format ax2
        ax2 = ax.twinx()

        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            ax2.plot(led_list.current_density_array_mean, led_list.wpe_array_mean, self.color_wheel[color_cnt], label = label)
            color_cnt = color_cnt + 1

        ax2.set_ylim(bottom=0)
        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")

    async def plot_allsizes_wpemax(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("size in [µm]")
        ax.set_ylabel("wpe max")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        from matplotlib.ticker import ScalarFormatter
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            dim = [first_led.LED_Dim_x * 10 ** 4]
            max_wpe = [max(led_list.wpe_array_mean)]
            #ax.plot(x='x', y='y', ax=ax, kind='scatter', label=label)
            ax.plot(dim, max_wpe, "black", label = label, markersize=10, marker="o")
            color_cnt = color_cnt + 1

        ax.set_ylim(bottom=2.4)
        ax.set_xlim(left=0.9)


        #plt.legend(loc="upper left")


        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")