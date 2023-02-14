import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import pdf_creator as pdfc
import led_properties
import LedList as ll
from numpy.polynomial import Polynomial
import math


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def format_e(n):
    a = '%E' % n
    b = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
    return f"{b:.{4}}"


class Auswertung:

    output_dir = "Output"
    single_plot_paths = []
    summary_plot_paths = []
    led_list = ll.LedList
    minimum_datapoints = 10
    limit_x_axis_density_begin = 10 ** 0
    limit_x_axis_density_end = 10 ** 4
    limit_x_axis_voltage_begin = 2.5
    limit_x_axis_voltage_end = 6

    def __init__(self, filepath, c: bool, v: bool):
        self.filepath = filepath
        self.c = c
        self.v = v

    async def build(self) -> str:
        return await self.plot_files(self.filepath)

    async def plot_files(self, filepath) -> str:
        syspath = filepath
        if syspath == "" or syspath == " ":
            return "no path provided"

        if not os.path.exists(syspath):
            return "provided path doesnt exist"

        if not os.path.exists(syspath + f"\\{self.output_dir}"):
            os.makedirs(syspath + f"\\{self.output_dir}")

        for file in os.listdir(syspath):
            if file.endswith(".csv"):
                file_name = file.title().replace(".Csv", "")
                file_name_split = file_name.split("____")

                if len(file_name_split) != 2:
                    continue

                date_time = file_name_split[0].replace("_", "-")
                measure_meta = file_name_split[1]

                # assignments
                measure_meta_split = measure_meta.split("_")
                if len(measure_meta_split) != 3:
                    continue

                led_no = int(measure_meta_split[0].replace("Q", ""))
                led_id = int(measure_meta_split[1].replace("Id", ""))
                edge_length = float(measure_meta_split[2].replace("D", ""))
                led_area = edge_length * edge_length
                led = led_properties.LED(led_no, led_area, led_id)

                with open(f'{syspath}/{file}', 'r') as f:
                    next(f)
                    u_mess_li = []
                    u_korr_li = []
                    i_soll_li = []
                    op_power_li = []
                    current_density_li = []
                    reader = csv.reader(f, delimiter=";")
                    cnt = 0

                    for row in reader:
                        if len(row) != 5:
                            continue
                        u_mess = float(row[0])
                        u_korr = float(row[1])
                        i_soll = float(row[2])
                        opt_power = float(row[3])
                        current_density = float(row[4]) * (4.0/np.pi)

                        # filter opt_power noise
                        # if(opt_power > 7*10E-10;100*opt_power/(volt*current);0)
                        if opt_power < 3*10**-8 or cnt < 10:
                            # opt_power = 100 * opt_power/(u_korr * i_mess)
                            opt_power = 0
                        else:
                            opt_power = opt_power


                        cnt = cnt + 1

                        # add data to lists
                        u_mess_li.append(u_mess)
                        u_korr_li.append(u_korr)
                        i_soll_li.append(i_soll)
                        op_power_li.append(opt_power)
                        current_density_li.append(current_density)

                print(f"datapoint cnt: {len(i_soll_li)} at LED: {led.led_no}")
                if len(i_soll_li) <= self.minimum_datapoints:
                    continue

                # add data to led object and calculate other properties
                led.add_data(u_mess_li, u_korr_li, i_soll_li, current_density_li, op_power_li)

                title = f"Q{led.led_no} ID{led.led_id} : " + str(led.LED_Dim_x) \
                        + " µm x " + str(led.LED_Dim_y) + " µm, WPE_max = " + str(
                    led.wpe_max) + " %, J_Max = " + str(led.j_max) + "A/cm²"

                if self.v:
                    await self.plot_save_v(f"{syspath}/{file}", led, title)
                if self.c:
                    await self.plot_save_c(f"{syspath}/{file}", led, title)

                self.single_plot_paths.clear()
                self.led_list.leds.append(led)

        if len(self.led_list.leds) == 0:
            return "no well formatted files found"

        first_led = self.led_list.leds[0]
        footer = f"{round(first_led.LED_Dim_x * 10 ** 4)} µm x {round(first_led.LED_Dim_y * 10 ** 4)} µm"

        # calc ax limits
        self.led_list.measurement_completed(self.led_list)
        self.limit_x_axis_voltage_end = max(self.led_list.voltage_array_mean)
        self.limit_x_axis_density_end = max(self.led_list.current_density_array_mean)
        op_idx = 0
        while self.led_list.op_power_array_mean[op_idx] == 0:
            op_idx = op_idx + 1
        self.limit_x_axis_density_begin = self.led_list.current_density_array_mean[op_idx+1]



        file = "output"
        file_footer = footer.replace(" ", "_")
        # plot the 4 summary plots
        await self.plot_save_c_sum(f"{syspath}/{file}_c_{file_footer}", "all LEDs " + footer)
        await self.plot_save_c_avg(f"{syspath}/{file}_c_{file_footer}_avg", "arithmetic mean and standard deviation " + footer)
        #await self.plot_save_c_fit(f"{syspath}/{file}_c_{file_footer}_fit", "curve fitting " + footer)
        await self.plot_save_sum_v(f"{syspath}/{file}_v_{file_footer}_sum", "all LEDs " + footer)
        await self.plot_save_avg_v(f"{syspath}/{file}_v_{file_footer}_avg", "arithmetic mean and standard deviation " + footer)

        # output path and filename for summary pdf
        pdf_summary_path = f"{self.filepath}/{self.output_dir}/summary_{file_footer}.pdf"

        # create the actual summary pdf
        header = f'Measurement report {date_time}'
        pdfc.PDF(header, footer).create_summary_pdf(self.summary_plot_paths, pdf_summary_path, f"Summary of {len(self.led_list.leds)} x {footer}",
                                                    self.led_list)

        # create csv
        csv_path = f'{syspath}/{self.output_dir}/_output.csv'
        self.led_list.create_csv(self.led_list, csv_path)

        return "finished"

    async def plot_save_c(self, file, led, title):
        array_x, array_y, array2_y = led.current_density_array[led.voltage_start_wpe_index:], led.op_power_array[led.voltage_start_wpe_index:], led.wpe_array[led.voltage_start_wpe_index:]
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        ax.plot(array_x, array_y, "k")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_yscale('log')
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)

        file = file.replace(".csv", "_c.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.single_plot_paths.append(path)

    async def plot_save_c_sum(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')

        for led in self.led_list.leds:
            if led.is_malfunctioning:
                continue
            ax.plot(led.current_density_array, led.op_power_array, "k")


        ax2 = ax.twinx()

        for led in self.led_list.leds:
            if led.is_malfunctioning:
                continue
            ax2.plot(led.current_density_array, led.wpe_array, 'b')

        ax2.set_xscale('log')
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)

        file = file.replace(".csv", "_c_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_c_fit(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))

        # format ax 1
        ax.set_title(title)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        op_power = np.array(self.led_list.op_power_array_mean)
        current_density = np.array(self.led_list.current_density_array_mean)
        wpe_array = np.array(self.led_list.wpe_array_mean)

        # limit for ax
        idx_density_start = find_nearest(current_density, self.limit_x_axis_density_begin)

        x = current_density[idx_density_start:]
        y = op_power[idx_density_start:]
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 3)
        y_fit = np.exp(np.polyval(p, logx))
        ax.plot(x, y_fit, c='blue')
        ax.scatter(x, y, marker='o', c='black')


        # limits for fitting ax2
        idx_wpe_max = wpe_array.argmax(axis=0)
        j_at_wpe_max = self.led_list.current_array_mean[idx_wpe_max] / self.led_list.leds[0].led_area
        n = 3
        start_idx = find_nearest(self.led_list.j_array_mean, j_at_wpe_max/n)
        end_idx = find_nearest(self.led_list.j_array_mean, j_at_wpe_max*n)
        print(f"start index = {start_idx} J = {self.led_list.current_array_mean[start_idx] / self.led_list.leds[0].led_area} A/cm^2")
        print(f"end index = {end_idx} J = {self.led_list.current_array_mean[end_idx] / self.led_list.leds[0].led_area} A/cm^2")

        # ax 2
        ax2 = ax.twinx()

        x = current_density[start_idx:end_idx]
        y = wpe_array[start_idx:end_idx]
        # scale is log, therefore log values
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 8)
        y_fit = lambda vlambda: np.exp(np.polyval(p, logx))
        ax2.plot(x, y_fit, c='blue')
        ax2.scatter(current_density[:start_idx], wpe_array[:start_idx], marker='o', c='blue')
        ax2.scatter(current_density[end_idx:], wpe_array[end_idx:], marker='o', c='blue')

        # format ax2
        ax2.grid(False)
        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        file = file.replace(".csv", "c_fit.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_c_avg(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        ax.errorbar(self.led_list.current_density_array_mean,
                    self.led_list.op_power_array_mean, self.led_list.op_power_array_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(self.led_list.current_density_array_mean, self.led_list.op_power_array_mean, s=4, linewidths=0.1, color='black')

        # format ax2
        ax2 = ax.twinx()

        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        ax2.errorbar(self.led_list.current_density_array_mean, self.led_list.wpe_array_mean, self.led_list.wpe_array_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(self.led_list.current_density_array_mean, self.led_list.wpe_array_mean, s=4, linewidths=0.1, color='blue')

        file = file.replace(".csv", "c_avg.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")


    async def plot_save_v(self, file, led, title):
        array_x, array_y, array2_y = led.voltage_korr_array, led.current_soll_array, led.op_power_array
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        ax.plot(array_x, array_y, "k")
        ax.set_yscale('log')
        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.grid(True)
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_yscale('log')
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)

        file = file.replace(".csv", "_v.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.single_plot_paths.append(path)

    async def plot_save_avg_v(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        ax.errorbar(self.led_list.voltage_array_mean,
                    self.led_list.current_array_mean, self.led_list.current_array_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(self.led_list.voltage_array_mean, self.led_list.current_array_mean, s=4, linewidths=0.1, color='black')
        ax.set_xlabel("Voltage [V]")
        ax.set_yscale('log')
        ax.set_ylabel("Current [A]")

        plt.xlim([self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end])

        ax.grid(True)
        ax2 = ax.twinx()
        ax2.errorbar(self.led_list.voltage_array_mean,
                     self.led_list.op_power_array_mean,  self.led_list.op_power_array_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(self.led_list.voltage_array_mean, self.led_list.op_power_array_mean, s=4, linewidths=0.1, color='blue')
        ax2.grid(False)
        ax2.set_yscale('log')
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_avg.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_sum_v(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        # plt.ylim([10**-7, 10**-4])

        for led in self.led_list.leds:
            if led.is_malfunctioning:
                continue
            ax.plot(led.voltage_korr_array, led.current_soll_array, "k")

        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.set_yscale('log')

        plt.xlim([self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end])

        ax.grid(True)
        ax2 = ax.twinx()
        for led in self.led_list.leds:
            if led.is_malfunctioning:
                continue
            ax2.plot(led.voltage_korr_array, led.op_power_array, 'b')

        ax2.grid(False)
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.set_yscale('log')

        file = file.replace(".csv", "_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")
