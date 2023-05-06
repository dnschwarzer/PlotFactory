import matplotlib.pyplot as plt
import auswertung_helper as static_m
import matplotlib.ticker as ticker
import numpy as np
import csv
from itertools import groupby
import itertools


class AuswertungExtensionMulti():

    color_wheel = ["black", "blue", "red", "green", "yellow", "cyan", "magenta", "black", "black", "black", "black"]
    marker_wheel = [",", "*", "o", "v", ">", "s", "p", "1", "2", "3", "<", "^", "."]

    def __init__(self, filepath, limit_den_be, limit_den_end, limit_vol_beg, limit_vol_end, summary):
        self.filepath = filepath
        self.limit_x_axis_density_begin = limit_den_be
        self.limit_x_axis_density_end = limit_den_end
        self.limit_x_axis_voltage_begin = limit_vol_beg
        self.limit_x_axis_voltage_end = limit_vol_end
        self.summary_plot_paths = summary
        self.fontsize = 25

    def find_min_op(self, led_lists):
        op_idx_li = []
        for led_list in led_lists:
            op_idx = 0
            while led_list.current_density_array_mean[op_idx] == 0:
                op_idx = op_idx + 1
            op_idx_li.append(led_list.current_density_array_mean[op_idx + 1])
        min_op = min(op_idx_li)
        return min_op

    #  csv_path = f'{folder}/{self.output_dir}/_output.csv'

    def is_comparable(self, size):
        if size == 100:
            return False, 0
        elif size == 50:
            return True, 20
        elif size == 50:
            return True, 20
        elif size == 50:
            return True, 20


    async def plot_save_c_avg(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        static_m.format_plot(plt, f"{title} area correction = {round(led_lists[0].area_correction, 2)}µm", ax, self.fontsize)
       # plt.xlim([self.find_min_op(led_lists), self.limit_x_axis_density_end])
        plt.xlim([2 * 10 ** -2, self.limit_x_axis_density_end])

       # plt.xlim([2 * 10 **-2, 1* 10**4])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
        color_cnt = 0
        static_m.scalar_formatter(ax)

        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
            color = "black"
            ax.plot(led_list.current_density_array_mean, led_list.op_power_array_mean, color=color, label = label, marker=self.marker_wheel[color_cnt], markersize="8")
            
            color_cnt = color_cnt + 1 if color_cnt < len(self.marker_wheel) - 2 else 0

        plt.legend(loc="upper left")
        static_m.format_plot(plt, title, ax, self.fontsize)

        file1 = file.replace(".csv", "_1.png")
        file_name1 = file1.split("/")[-1]
        path1 = f"{self.filepath}/{file_name1}_1_corr_{led_list.area_correction}.png"
        fig.savefig(path1)

        # format ax2
        fig, ax2 = plt.subplots(figsize=(24, 16))
        static_m.format_plot(plt, title, ax2, self.fontsize)
        plt.xlim([1 * 10 ** -3, 10 ** 3])
        #plt.xlim([2 * 10 ** -2, self.limit_x_axis_density_end])
      #  plt.xlim([2 * 10 ** -2, 1 * 10 ** 4])
        ax2.set_xscale('log')
        ax2.grid(which='major', linestyle='-')
        ax2.grid(which='minor', linestyle='--')
        ax2.grid(True)

        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("EQE", fontsize=self.fontsize)
        #static_m.scalar_formatter(ax2)

        color_cnt = 0


        max_100um = max(led_lists[0].wpe_array_mean)
        normalize = (max_100um / 0.121)
        dens_at_wpe_max = led_lists[0].current_density_array_mean[static_m.find_nearest(led_lists[0].wpe_array_mean, max_100um)]

        line_list = []
        for led_list in led_lists:

            first_led = led_list.leds[0]
            size = round(led_list.edge_length, 2)
            label = f"{size}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
            color = "green" if first_led.led_no == "unknown" else "black"
            color = "black"

            if size == 100:
                color = "green"
                line_list.append(label)
            elif size == 50:
                color = "blue"
            elif size == 15:
                color = "magenta"


            ax2.plot(np.asarray(led_list.current_density_array_mean) / dens_at_wpe_max, np.asarray(led_list.wpe_array_mean) / normalize, color=color, label=label, marker=self.marker_wheel[color_cnt], markersize="8")
            color_cnt = color_cnt + 1

        cea_list = []
        color_cnt = 0


        cea_eqe_maxes = []

        #ax2.set_ylim(bottom=0.5)
        ax2.set_ylim(bottom=0.05)
        plt.legend(loc="upper left")

        file2 = file.replace(".csv", "_2.png")
        file_name2 = file2.split("/")[-1]
        path2 = f"{self.filepath}/{file_name2}_2_corr_{led_list.area_correction}.png"
        fig.savefig(path2)
        #self.summary_plot_paths.append(f"{path}.png")


    async def plot_save_iqe(self, file, title, led_lists):
       # array_x, array_y = led.j_array, led.eqe_array
        array_x, array_y = led_lists.j_array_mean, led_lists.eqe_array_mean
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)

        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True
        delta = 0.01
        A = led.iqe_max
        B = led.j_at_wpe_max
        # print(f"j max = {B}")

        xrange = np.geomspace(0.1, 10 ** 8, 50)
        yrange = np.geomspace(0.01, A + 0.1, 50)

        x, y = np.meshgrid(xrange, yrange)
        equation = 1 - (((1 - A) / (2 * x)) * (1 + (y * x) / (A * B)) * np.sqrt(y * x * B / A)) - y  # x = J, y = IQE
        plt.contour(x, y, equation, [0], colors="black")
        plt.xscale("log")
        plt.grid(which='major', linestyle='-')
        plt.grid(which='minor', linestyle='--')

        ax.set_xlabel("J [A/cm²]", fontsize=self.fontsize)
        ax.set_ylabel("IQE", fontsize=self.fontsize)
        ax.grid(True)
        ax.set_ylim([0, led.iqe_max])

        y_fit = np.polyval(led.eqe_fit_coeff, xrange)
        # print(f"eqe p : {led.eqe_fit_coeff}")

        ax2 = ax.twinx()
        ax2.plot(array_x, array_y, 'b')
        ax2.set_xscale('log')
        ax2.set_xlabel("J [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("EQE", fontsize=self.fontsize)
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)
        ax2.set_ylim([0, max(array_y)])
        static_m.scalar_formatter(ax2)


        file = file.replace(".csv", "_iqe.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_allsizes_wpemax(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        area_correction = " area correction = {round(led_lists[0].area_correction, 2)}µm"
        static_m.format_plot(plt, f"{title} ", ax, self.fontsize)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
       # ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("size in [µm]", fontsize=self.fontsize)
        ax.set_ylabel("WPE_max", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
        static_m.scalar_formatter(ax)

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]


            label = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
            dim = [first_led.LED_Dim_x * 10 ** 4]
            rounddim = round(first_led.LED_Dim_x * 10 ** 4)
            max_wpe = [max(led_list.wpe_array_mean)] if rounddim != 5 and rounddim != 50 else led_list.wpe_abs_max
           # print(f"dim {dim} max wpe = {max_wpe}")


            #ax.plot(x='x', y='y', ax=ax, kind='scatter', label=label)
            #color = "green" if first_led.led_no == "unknown" else "black"
            color = "black"
            ax.plot(dim, max_wpe, color, label = label, markersize=10, marker="o")
            color_cnt = color_cnt + 1

        
        #ax.set_ylim(bottom=1.0)
        #ax.set_ylim(top=(max(wpe_maxes) + 0.5))
        #ax.set_xlim(left=0.9)
       # ax.xaxis.set_major_locator(ticker.LogLocator(subs=range(1,10)))


        #plt.legend(loc="upper left")


        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}_corr_{led_list.area_correction}.png"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")


    async def plot_allsizes_wpemax_aspect_ratio(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        area_correction = " area correction = {round(led_lists[0].area_correction, 2)}µm"
        static_m.format_plot(plt, f"{title} ", ax, self.fontsize)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
      #  ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("aspect ratio", fontsize=self.fontsize)
        ax.set_ylabel("WPE_max", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
       # static_m.scalar_formatter(ax)
       # ax.ticklabel_format(useOffset=False)

        # create a sorted copy of the `led_list` using slicing or the `copy` method
        led_list_sorted = led_lists.copy() # or led_list.copy()

        # sort the copied list by their `area` attribute
        led_list_sorted.sort(key=lambda x: x.area)

        # use itertools.groupby to group the objects by their `area` attribute
        led_groups = []
        for area, led_group in itertools.groupby(led_list_sorted, key=lambda x: x.area):
            led_groups.append(list(led_group))

        wpe_maxes = []

        aspects = [ 1/1, 1/3, 1/5, 1/10, 1/20]
        aspect_ticks = [ 1/1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9, 1/10, 1/18 , 1/20]

        for groups in led_groups:
            x = []
            y = []
            i = 0
            for group in groups:
                ratio = aspects[i] 
                x.append(ratio)
                i = i + 1
                wpe_max = max(group.wpe_array_mean)
                y.append(wpe_max) 
                wpe_maxes.append(wpe_max)

            ax.plot(x, y, label = f"({int(groups[0].edge_length)})² µm²", markersize=10, marker="o")

        plt.gca().invert_xaxis()       
        ax.set_ylim(bottom=1.5)
        ax.set_ylim(top=(max(wpe_maxes) + 0.5))
        plt.legend(loc="upper right")

        ax.set_xscale('log')
        asp_l = []
        for aspect in aspect_ticks:
            asp_l.append(f"1:{(int(1.0/float(aspect)))}")

        ax.set_xticks(aspect_ticks, labels=asp_l)
        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}_corr_{led_lists[0].area_correction}.png"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")

    async def plot_allsizes_wpe_wpemax_normalized(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        area_correction = " area correction = {round(led_lists[0].area_correction, 2)}µm"
        static_m.format_plot(plt, f"{title} ", ax, self.fontsize)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("size in [µm]", fontsize=self.fontsize)
        ax.set_ylabel("WPE_max/WPE_max_100um", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
        static_m.scalar_formatter(ax)

        wpe_maxes = []
        for led_list in led_lists:
            wpe_maxes.append(max(led_list.wpe_array_mean))

        color_cnt = 0

        cea_wpe_maxes = [0.12, 0.117, 0.11, 0.104, 0.10]
        cea_sizes = [100, 50, 20, 15, 10]

        # ax2.scatter(5*10 ** 0 , 0.121, color="green", label="CEA 100µm", marker="x", s=100)
        # ax2.scatter(8*10 ** 0, 0.117, color="blue", label="CEA 50µm", marker="x", s=100)
        # ax2.scatter(2*10 ** 1, 0.104, color="magenta", label="CEA 15µm", marker="x", s=100)

        normalized = max(led_lists[0].wpe_array_mean) / 100
        normalized_cea = cea_wpe_maxes[0] / 100

        dim_array = []
        max_array = []

        for led_list in led_lists:
            first_led = led_list.leds[0]

            label = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
            dim = [first_led.LED_Dim_x * 10 ** 4]
            rounddim = round(first_led.LED_Dim_x * 10 ** 4)
            max_wpe = [max(led_list.wpe_array_mean)] if rounddim != 5 and rounddim != 50 else led_list.wpe_abs_max
           # print(f"dim {dim} max wpe = {max_wpe}")
            max_wpe = np.asarray(max_wpe) / normalized
            #ax.plot(x='x', y='y', ax=ax, kind='scatter', label=label)
            #color = "green" if first_led.led_no == "unknown" else "black"
            color = "black"
            label = "QD"
            dim_array.append(dim)
            max_array.append(max_wpe)
            if color_cnt == 0:
                label = "QD"
            else:
                label = None
          #  ax.plot(dim, max_wpe, color, label = label,  ,markersize=10, marker="o")
            ax.plot(dim, max_wpe, color, label = label, color="#f74a50" ,markersize=10, marker="o")
            color_cnt = color_cnt + 1

        ax.plot(dim_array, max_array, color="#f74a50", label = label,  marker=",")
        label = "CEA"
        for i in range(0, len(cea_wpe_maxes)):
            if i == 0:
                label = "CEA"
            else:
                label = None
            ax.plot([cea_sizes[i]], [cea_wpe_maxes[i] / normalized_cea], label=label, markersize=8, color="purple", marker="o", zorder=10)
        ax.plot(cea_sizes, np.asarray(cea_wpe_maxes) / normalized_cea, color="purple", label = label,  marker=",")

        plt.legend(loc="upper left")

        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}_corr_{led_list.area_correction}.png"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")


    async def plot_allsizes_iqemax(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        static_m.format_plot(plt, f"{title} area correction = {round(led_lists[0].area_correction, 2)}µm", ax, self.fontsize)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("size in [µm]", fontsize=self.fontsize)
        ax.set_ylabel("IQE_max", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
        static_m.scalar_formatter(ax)

        iqe_maxes = []
        for led_list in led_lists:
            iqe_maxes.append(led_list.iqe_max_mean * 10 ** 2)

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
            dim = [first_led.LED_Dim_x * 10 ** 4]
            rounddim = round(first_led.LED_Dim_x * 10 ** 4)
           # print(f"dim {dim} max wpe = {max_wpe}")

            #ax.plot(x='x', y='y', ax=ax, kind='scatter', label=label)
            #color = "green" if first_led.led_no == "unknown" else "black"
            color = "black"
            ax.plot(dim, led_list.iqe_max_mean * 10 ** 2, color, label = label, markersize=10, marker="o")
            color_cnt = color_cnt + 1
        ax.set_ylim(top=(max(iqe_maxes) + 10))

        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}_corr_{led_list.area_correction}.png"
        fig.savefig(path)


    def create_csv(self, paths, led_lists):

        with open(paths[0], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n', delimiter=";")
            cols = []
            for led_list in led_lists:
                descrp = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
                cols.append("Current Density [A/cm²] " + descrp)
                cols.append(descrp)


            row = cols
            writer.writerow(row)
            lists = []

            for led_list in led_lists:
                lists.append(led_list.current_density_array_mean)

            max_entries = len(max(lists, key=len))
            # padding
            for led_list in led_lists:
                len_of_dens = len(led_list.current_density_array_mean)
                for cnt in range(0, max_entries - len_of_dens):
                    led_list.current_density_array_mean.append("")
                len_of_opt = len(led_list.op_power_array_mean)
                for cnt in range(0, max_entries - len_of_opt):
                    led_list.op_power_array_mean.append("")

            for item in range(0, max_entries):
                row = []
                for led_list in led_lists:
                    row.append(led_list.current_density_array_mean[item])
                    row.append(led_list.op_power_array_mean[item])


                writer.writerow(row)
                row.clear()

        with open(paths[1], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n', delimiter=";")
            cols = []
            for led_list in led_lists:
                descrp = f"{round(led_list.edge_length, 2)}µm {led_list.geometric} R 1:{round(led_list.ratio, 2)} {led_list.color}"
                cols.append("Current Density [A/cm²] " + descrp)
                cols.append(descrp)

            row = cols
            writer.writerow(row)

            lists = []
            for led_list in led_lists:
                lists.append(led_list.current_density_array_mean)

            max_entries = len(max(lists, key=len))

            for led_list in led_lists:
                len_of_dens = len(led_list.current_density_array_mean)
                for cnt in range(0, max_entries - len_of_dens):
                    led_list.current_density_array_mean.append("")
                len_of_wpe = len(led_list.wpe_array_mean)
                for cnt in range(0, max_entries - len_of_wpe):
                    led_list.wpe_array_mean.append("")

            for item in range(0, max_entries):
                row = []
                for led_list in led_lists:
                    row.append(led_list.current_density_array_mean[item])
                    row.append(led_list.wpe_array_mean[item])

                writer.writerow(row)
                row.clear()

    def create_overview_csv(self, paths, led_lists):
        with open(f"{paths[0]}", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n', delimiter=";")
            cols = []
            writer.writerow(["size", "IQE_max", "WPE_max" ])
            for led_list in led_lists:
                descrp = f"{round(led_list.edge_length, 2)}"
                cols.append(descrp)
                cols.append(f"{led_list.iqe_max_mean * 10 ** 2}")
                max_wpe = max(led_list.wpe_array_mean)
                cols.append(f"{max_wpe}")

                row = cols
                writer.writerow(row)
                row.clear()
                cols.clear()
