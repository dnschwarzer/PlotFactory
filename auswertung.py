import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from typing import List
import pdf_creator as pdfc
import led_properties
import LedList as ll
from numpy.polynomial import Polynomial


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
                date_time = file_name.split("____")[0].replace("_", "-")
                measure_meta = file_name.split("____")[1]

                # assignments
                led_no = int(measure_meta.split("_")[0].replace("Q", ""))
                led_id = int(measure_meta.split("_")[1].replace("Id", ""))
                led_area = float(measure_meta.split("_")[2].replace("D", ""))
                led = led_properties.LED(led_no, led_area, led_id)

                with open(f'{syspath}/{file}', 'r') as f:
                    next(f)
                    u_mess_li = []
                    u_korr_li = []
                    i_soll_li = []
                    op_power_li = []
                    current_density_li = []
                    reader = csv.reader(f, delimiter=";")

                    for row in reader:
                        u_mess = float(row[0])
                        u_korr = float(row[1])
                        i_soll = float(row[2])
                        opt_power = float(row[3])
                        current_density = float(row[4])

                        # filter opt_power noise
                        # if(opt_power > 7*10E-10;100*opt_power/(volt*current);0)
                        if opt_power > 7 * 10 ** -10:
                            # opt_power = 100 * opt_power/(u_korr * i_mess)
                            opt_power = opt_power
                        else:
                            opt_power = 0

                        # add data to lists
                        u_mess_li.append(u_mess)
                        u_korr_li.append(u_korr)
                        i_soll_li.append(i_soll)
                        op_power_li.append(opt_power)
                        current_density_li.append(current_density)

                # add data to led object and calculate other properties

                led.add_data(u_mess_li, u_korr_li, i_soll_li, current_density_li, op_power_li)

                title = f"Q{led.led_no} ID{led.led_id} : " + str(led.LED_Dim_x) + " µm x " + str(led.LED_Dim_y) + " µm, WPE_max = " + str(
                    led.wpe_max) + " %, J_Max = " + str(led.j_max) + "A/cm²"

                if self.v:
                    await self.plot_save_v(f"{syspath}/{file}", led, title)
                if self.c:
                    await self.plot_save_c(f"{syspath}/{file}", led, title)

                self.single_plot_paths.clear()
                self.led_list.leds.append(led)

        self.led_list.measurement_completed(self.led_list)

        # plot the 4 summary plots
        await self.plot_save_c_sum(f"{syspath}/{file}_c_sum", self.led_list.current_density_array, self.led_list.op_power_array, self.led_list.wpe_array, "all LEDs")
        await self.plot_save_c_avg(f"{syspath}/{file}_c_avg", self.led_list.current_density_array, self.led_list.op_power_array, self.led_list.wpe_array, "arithmetic mean and standard deviation")
        await self.plot_save_c_fit(f"{syspath}/{file}_c_fit", self.led_list.current_density_array, self.led_list.op_power_array, self.led_list.wpe_array, "arithmetic mean and standard deviation")
        await self.plot_save_sum_v(f"{syspath}/{file}_v_sum", self.led_list.voltage_array, self.led_list.current_array, self.led_list.op_power_array, "all LEDs")
        await self.plot_save_avg_v(f"{syspath}/{file}_v_avg", self.led_list.voltage_array, self.led_list.current_array, self.led_list.op_power_array, "arithmetic mean and standard deviation")

        # output path and filename for summary pdf
        pdf_summary_path = f"{self.filepath}/{self.output_dir}/summary.pdf"

        # create the actual summary pdf
        first_led = self.led_list.leds[0]
        footer = str(format_e(first_led.LED_Dim_x)) + " µm x " + str(format_e(first_led.LED_Dim_y)) + " µm"
        header = f'Measurement report {date_time}'
        pdfc.PDF(header, footer).create_summary_pdf(self.summary_plot_paths, pdf_summary_path, "Summary",
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

        file = file.replace(".csv", "_c.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.single_plot_paths.append(path)

    async def plot_save_c_sum(self, file, current_density, op_power, wpe_array, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        plt.xlim([10 ** 0, 10 ** 4])

        data_points = len(current_density)
        for idx in range(0, data_points):
            ax.plot(current_density[idx], op_power[idx], "k")

        ax.set_xscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax2 = ax.twinx()

        for x in range(0, len(current_density)):
            ax2.plot(current_density[x], wpe_array[x], 'b')

        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_c_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_c_fit(self, file, array_x, array_y, array2_y, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title("curve fitting")
        plt.xlim([10 ** 0, 10 ** 4])
        # self.current_density_array_sum, self.op_power_array_sum_c, self.wpe_array_sum
        current_density = []
        op_power = []
        wpe_array = []
        average_c = []
        average_v = []
        average_p = []

        data_points = len(min(array_y, key=len))
        led_cnt = len(array_y)

        for idx in range(0, data_points):
            for led in range(0, led_cnt):
                average_c.append(array_y[led][idx])
                average_v.append(array_x[led][idx])
                average_p.append(array2_y[led][idx])

            current_density.append(np.mean(average_c))
            average_c.clear()

            op_power.append(np.mean(average_v))
            average_v.clear()

            wpe_array.append(np.mean(average_p))
            average_p.clear()

        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.set_xscale('log')

        op_power = np.array(op_power)
        current_density = np.array(current_density)
        wpe_array = np.array(wpe_array)

        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        x = op_power
        y = current_density
        p = Polynomial.fit(x, y, 3)
        ax.plot(*p.linspace(), c='black')
        ax.scatter(x, y, marker='o', c='black')

        ax2 = ax.twinx()
        x = op_power
        y = wpe_array
        p = Polynomial.fit(x, y, 2)
        ax2.plot(*p.linspace(), c='blue')
        ax2.scatter(x, y, marker='o', c='blue')
        ax2.grid(True)

        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "c_fit.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_v(self, file, led, title):
        array_x, array_y, array2_y = led.voltage_korr_array, led.current_soll_array, led.op_power_array
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        ax.plot(array_x, array_y, "k")
        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.grid(True)
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_v.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.single_plot_paths.append(path)

    async def plot_save_c_avg(self, file, array_x, array_y, array2_y, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        plt.xlim([10 ** 0, 10 ** 4])

        currents = []
        currents_std = []
        voltages = []
        voltages_std = []
        op_power = []
        op_power_std = []
        average_c = []
        average_v = []
        average_p = []

        data_points = len(min(array_y, key=len))
        led_cnt = len(array_y)

        for idx in range(0, data_points):
            for led in range(0, led_cnt):
                average_c.append(array_y[led][idx])
                average_v.append(array_x[led][idx])
                average_p.append(array2_y[led][idx])

            currents.append(np.mean(average_c))
            currents_std.append(np.std(average_c))
            average_c.clear()

            voltages.append(np.mean(average_v))
            voltages_std.append(np.std(average_v))
            average_v.clear()

            op_power.append(np.mean(average_p))
            op_power_std.append(np.std(average_p))
            average_p.clear()

        ax.errorbar(voltages, currents, currents_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(voltages, currents, s=4, linewidths=0.1, color='black')

        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.set_xscale('log')
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax.xaxis, ax.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        ax2 = ax.twinx()
        ax2.errorbar(voltages, op_power, op_power_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(voltages, op_power, s=4, linewidths=0.1, color='blue')

        # ax2.plot(voltages, op_power, 'b')

        ax2.grid(False)

        ax2.set_xscale('log')

        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "c_avg.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_avg_v(self, file, voltage_array, current_array, op_power_array, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)

        currents = []
        currents_std = []
        voltages = []
        voltages_std = []
        opPower = []
        opPower_std = []
        average_c = []
        average_v = []
        average_p = []

        data_points = len(current_array[0])
        led_cnt = len(current_array)

        for point in range(0, data_points):
            for led in range(0, led_cnt):
                average_c.append(current_array[led][point])
                average_v.append(voltage_array[led][point])
                average_p.append(op_power_array[led][point])

            currents.append(np.mean(average_c))
            currents_std.append(np.std(average_c))
            average_c.clear()

            voltages.append(np.mean(average_v))
            voltages_std.append(np.std(average_v))
            average_v.clear()

            opPower.append(np.mean(average_p))
            opPower_std.append(np.std(average_p))
            average_p.clear()

        # plt.ylim([5 * 10**-8, 10**-2])
        ax.errorbar(voltages, currents, currents_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(voltages, currents, s=4, linewidths=0.1, color='black')
        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        plt.xlim([2.5, 6])

        ax.grid(True)
        ax2 = ax.twinx()
        ax2.errorbar(voltages, opPower, opPower_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(voltages, opPower, s=4, linewidths=0.1, color='blue')
        ax2.grid(True)
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_avg.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_sum_v(self, file, array_x, array_y, array2_y, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        # plt.ylim([10**-7, 10**-4])

        for x in range(0, len(array_x)):
            ax.plot(array_x[x], array_y[x], "k")

        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        plt.xlim([2.5, 6])

        ax.grid(True)
        ax2 = ax.twinx()
        for x in range(0, len(array_x)):
            ax2.plot(array_x[x], array2_y[x], 'b')

        ax2.grid(True)
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")
