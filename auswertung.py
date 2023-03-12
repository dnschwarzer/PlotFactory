import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import pdf_creator as pdfc
import led_properties
import LedList
from _auswertung_single import AuswertungExtensionSingle as Single
from _auswertung_multi import AuswertungExtensionMulti as Multi
import math
import scipy.optimize as opt
import scipy
import auswertung_helper as static_m

import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)

def format_e(n):
    a = '%E' % n
    b = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
    return f"{b:.{4}}"


class Auswertung:

    output_dir = "Output"
    single_plot_paths = []
    summary_plot_paths = []
    led_list = LedList.LedList()
    list_of_measurements = []
    minimum_datapoints = 10
    limit_x_axis_density_begin = 10 ** 0
    limit_x_axis_density_end = 10 ** 4
    limit_x_axis_voltage_begin = 2.5
    limit_x_axis_voltage_end = 6

    def __init__(self, filepath, do_pixel_plot: bool, do_array_plot: bool, do_summary_plot: bool):
        self.filepath = filepath
        self.do_pixel_plot = do_pixel_plot
        self.do_array_plot = do_array_plot
        self.do_summary_plot = do_summary_plot
        self.fontsize = 25

    async def build(self) -> str:
        return await self.plot(self.filepath)

    async def plot(self, filepath) -> str:
        syspath = filepath
        if syspath == "" or syspath == " ":
            return "no path provided"

        if not os.path.exists(syspath):
            return "provided path doesnt exist"

        subfolders = [f.path for f in os.scandir(syspath) if f.is_dir()]

        for folder in subfolders:
            if not os.path.exists(folder + f"\\{self.output_dir}"):
                os.makedirs(folder + f"\\{self.output_dir}")

            self.summary_plot_paths.clear()
            current_led_list = LedList.LedList()

            for file in os.listdir(folder):
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

                    with open(f'{folder}/{file}', 'r') as f:
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

                    # print(f"datapoint cnt: {len(i_soll_li)} at LED: {led.led_no}")
                    if len(i_soll_li) <= self.minimum_datapoints:
                        continue

                    # add data to led object and calculate other properties
                    led.add_data(u_mess_li, u_korr_li, i_soll_li, current_density_li, op_power_li)
                    current_led_list.leds.append(led)

                    title = f"Q{led.led_no} ID{led.led_id} : " + str(round(led.LED_Dim_y * 10 ** 4)) \
                            + " µm x " + str(round(led.LED_Dim_y * 10 ** 4)) + " µm, WPE_max = " + str(
                        led.wpe_max) + " %, J_Max = " + str(led.j_max) + "A/cm²"

                    if self.do_pixel_plot:
                        await self.plot_save_v(f"{folder}/{self.output_dir}/{file}", led, title)
                        await self.plot_save_c(f"{folder}/{self.output_dir}/{file}", led, title)
                        await self.plot_save_e(f"{folder}/{self.output_dir}/{file}", led, title)
                        await self.plot_save_f(f"{folder}/{self.output_dir}/{file}", led, title)
                        await self.plot_save_iqe(f"{folder}/{self.output_dir}/{file}", led, title)
                        self.single_plot_paths.clear()

            if len(current_led_list.leds) == 0:
                return "no well formatted files found"

            first_led = current_led_list.leds[0]
            footer = f"{round(first_led.LED_Dim_x * 10 ** 4)}x{round(first_led.LED_Dim_y * 10 ** 4)} µm"
            file_footer = footer.replace(" ", "_")

            # calc ax limits
            current_led_list.measurement_completed()
            self.limit_x_axis_voltage_end = max(current_led_list.voltage_array_mean)
            self.limit_x_axis_density_end = max(current_led_list.current_density_array_mean)
            op_idx = 0
            while current_led_list.op_power_array_mean[op_idx] == 0:
                op_idx = op_idx + 1
            self.limit_x_axis_density_begin = current_led_list.current_density_array_mean[op_idx+1]

            self.list_of_measurements.append(current_led_list)
            if self.do_array_plot:
                # outsourcing extension methods
                single = Single(current_led_list, folder, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

                # plot the 4 summary plots
                await single.plot_save_c_sum(f"{folder}/{self.output_dir}/{file_footer}_c_sum", "all LEDs " + footer, current_led_list)
                await single.plot_save_c_avg(f"{folder}/{self.output_dir}/{file_footer}_c_avg", "arithmetic mean and standard deviation " + footer, current_led_list)
                #await single.plot_save_c_fit(f"{folder}/{self.output_dir}/{file_footer}_c_fit", "curve fitting " + footer)
                await single.plot_save_sum_v(f"{folder}/{self.output_dir}/{file_footer}_v_sum", "all LEDs " + footer, current_led_list)
                await single.plot_save_avg_v(f"{folder}/{self.output_dir}/{file_footer}_v_avg",  footer, current_led_list)

                # output path and filename for summary pdf
                pdf_summary_path = f"{folder}/{self.output_dir}/summary_{file_footer}.pdf"

                # create the actual summary pdf
                header = f'Measurement report {date_time}'
                pdfc.PDF(header, footer).create_summary_pdf(self.summary_plot_paths, pdf_summary_path, f"Summary of {len(current_led_list.leds)} x {footer}",
                                                            current_led_list)

                # create csv
                csv_path = f'{folder}/{self.output_dir}/_output.csv'
                current_led_list.create_csv(csv_path)


        # all measurements
        # sort for size
        self.list_of_measurements.sort(key=lambda x: x.area, reverse=True)
        multi = Multi(self.filepath, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

        if self.do_summary_plot:
            await multi.plot_save_c_avg(f"{syspath}_wpe_overview", "all sizes ", self.list_of_measurements)
            await multi.plot_allsizes_wpemax(f"{syspath}_wpe_max_all_sizes", "wpe max overview", self.list_of_measurements)

        return "finished"

    async def plot_save_c(self, file, led, title):
        array_x, array_y, array2_y = led.current_density_array[led.voltage_start_wpe_index:], \
                                     led.op_power_array[led.voltage_start_wpe_index:], \
                                     led.wpe_array[led.voltage_start_wpe_index:]
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)
        ax.plot(array_x, array_y, "k")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_yscale('log')
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        static_m.scalar_formatter(ax)
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]")
        ax2.set_ylabel("WPE [%]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)
        static_m.scalar_formatter(ax2)


        file = file.replace(".csv", "_c.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_save_v(self, file, led, title):
        array_x, array_y, array2_y = led.voltage_korr_array, led.current_soll_array, led.op_power_array
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)
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
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_save_e(self, file, led, title):
        array_x, array_y = led.current_soll_array, led.eqe_array
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)

        idx_wpe_max = array_y.argmax(axis=0)
        j_at_wpe_max = led.current_soll_array[idx_wpe_max] / led.led_area
        n = 3
        start_idx = static_m.find_nearest(led.j_array, j_at_wpe_max / n)
        end_idx = static_m.find_nearest(led.j_array, j_at_wpe_max * n)

        x = array_x[start_idx:end_idx]
        y = array_y[start_idx:end_idx]

        # scale is log, therefore log values
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 8)
        x3 = np.linspace(x[0], x[-1], 80)
        logx3 = np.log(x3)
        y3 = np.exp(np.polyval(p, logx3))
        ax.scatter(x3, y3, c='green')

        y_fit = np.exp(np.polyval(p, logx))
        # ax.scatter(x, y_fit, c='blue')

        ax.plot(array_x, array_y, "k")
        ax.set_xscale('log')
        ax.set_xlabel("Current [A]")
        ax.set_ylabel("EQE")
        ax.grid(True)

        file = file.replace(".csv", "_e.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_save_iqe(self, file, led, title):
        array_x, array_y = led.j_array, led.eqe_array
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)

        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True
        delta = 0.01
        A = led.iqe_max
        B = led.j_at_wpe_max
        # print(f"j max = {B}")

        xrange = np.geomspace(0.1, 10 ** 5, 50)
        yrange = np.geomspace(0.01, A + 0.1, 50)

        x, y = np.meshgrid(xrange, yrange)
        equation = 1 - (((1 - A) / (2 * x)) * (1 + (y * x) / (A * B)) * np.sqrt(y * x * B / A)) - y  # x = J, y = IQE
        plt.contour(x, y, equation, [0], colors="black")
        plt.xscale("log")
        plt.grid(b=True, which='major', linestyle='-')
        plt.grid(b=True, which='minor', linestyle='--')

        ax.set_xlabel("J [A/cm²]")
        ax.set_ylabel("IQE")
        ax.grid(True)
        ax.set_ylim([0, led.iqe_max])

        y_fit = np.polyval(led.eqe_fit_coeff, xrange)
        # print(f"eqe p : {led.eqe_fit_coeff}")

        ax2 = ax.twinx()
        ax2.plot(array_x, array_y, 'b')
        ax2.set_xscale('log')
        ax2.set_xlabel("J [A/cm²]")
        ax2.set_ylabel("EQE")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)
        ax2.set_ylim([0, max(array_y)])
        static_m.scalar_formatter(ax2)


        file = file.replace(".csv", "_iqe.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_save_f(self, file, led, title):
        if led.is_malfunctioning:
            return

        array_x, array_y = led.p_array, led.eqe_array
        # only values after wpe max
        idx_eqe = static_m.find_nearest(led.eqe_array, led.eqe_max)
        array_x2 = led.p_array[:idx_eqe]
        array_y2 = led.eqe_array[:idx_eqe]

        array_x = array_x[idx_eqe:]
        array_y = array_y[idx_eqe:]

        sqrt_p_array = []
        sqrt_p_inv_array = []
        sqrt_p_inv_array2 = []
        sqrt_p_array2 = []

        for val in array_x2:
            sqrt_p_array2.append(math.sqrt(val))
            sqrt_p_inv_array2.append(1.0 / math.sqrt(val))

        for val in array_x:
            sqrt_p_array.append(math.sqrt(val))
            sqrt_p_inv_array.append(1.0/math.sqrt(val))

        array_x = np.add(sqrt_p_array, sqrt_p_inv_array)
        array_x2 = np.add(sqrt_p_array2, sqrt_p_inv_array2)
        array_y = led.eqe_max / array_y
        array_y2 = led.eqe_max / array_y2
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)

        if len(array_x) > 0:

            end_idx = static_m.find_nearest(array_x, 8)
            x = array_x[:end_idx]
            y = array_y[:end_idx]

            if not len(x) <= 0 and np.isfinite(x).all() and np.isfinite(y).all():
                q_func = lambda x_param, q: (q + x_param) / (q + 2)
                popt, pcov = scipy.optimize.curve_fit(q_func, x, y)
                # more x vals
                xfine = np.linspace(array_x[0], array_x[-1], 100)
                y_fitted = q_func(xfine, popt[0])
                # print(f"LED: {led.led_no}  Q {popt[0]} pcov:{pcov[0]}")
                ax.scatter(xfine, y_fitted, c='green')

        static_m.scalar_formatter(ax)

        ax.plot(array_x, array_y, "k")
        ax.plot(array_x2, array_y2, "blue")
        ax.set_xlabel(f"sqrt(P) + 1/sqrt(P)| fit param: x0:{x[0]}, x_end:{x[-1]}, Q={popt[0]}, covar={pcov[0]}, IQE_max ={(popt[0]/(popt[0]+2))*10**2}%")
        ax.set_ylabel("EQE_max / EQE")
        ax.grid(True)

        file = file.replace(".csv", "_f.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

