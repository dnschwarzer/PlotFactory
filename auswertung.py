import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import pdf_creator as pdfc
import led_properties
import LedList
from _auswertung import AuswertungExtensionSingle as Single
from _auswertung_multi import AuswertungExtensionMulti as Multi
from numpy.polynomial import Polynomial
import math
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt


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
    led_list = LedList.LedList()
    list_of_measurements = []
    minimum_datapoints = 10
    limit_x_axis_density_begin = 10 ** 0
    limit_x_axis_density_end = 10 ** 4
    limit_x_axis_voltage_begin = 2.5
    limit_x_axis_voltage_end = 6

    def __init__(self, filepath, c: bool, v: bool, multi: bool):
        self.filepath = filepath
        self.c = c
        self.v = v
        self.multi = multi

    async def build(self) -> str:
        if not self.multi:
            return await self.plot_files(self.filepath)
        return await self.plot_multi(self.filepath)

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

        # outsourcing extension methods
        single = Single(self.led_list, self.filepath, self.output_dir, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

        # plot the 4 summary plots
        await single.plot_save_c_sum(f"{syspath}/{file}_c_{file_footer}", "all LEDs " + footer)
        await single.plot_save_c_avg(f"{syspath}/{file}_c_{file_footer}_avg", "arithmetic mean and standard deviation " + footer)
        #await single.plot_save_c_fit(f"{syspath}/{file}_c_{file_footer}_fit", "curve fitting " + footer)
        await single.plot_save_sum_v(f"{syspath}/{file}_v_{file_footer}_sum", "all LEDs " + footer)
        await single.plot_save_avg_v(f"{syspath}/{file}_v_{file_footer}_avg", "arithmetic mean and standard deviation " + footer)

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


    async def plot_multi(self, filepath) -> str:
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

                    print(f"datapoint cnt: {len(i_soll_li)} at LED: {led.led_no}")
                    if len(i_soll_li) <= self.minimum_datapoints:
                        continue

                    # add data to led object and calculate other properties
                    led.add_data(u_mess_li, u_korr_li, i_soll_li, current_density_li, op_power_li)

                    title = f"Q{led.led_no} ID{led.led_id} : " + str(led.LED_Dim_x) \
                            + " µm x " + str(led.LED_Dim_y) + " µm, WPE_max = " + str(
                        led.wpe_max) + " %, J_Max = " + str(led.j_max) + "A/cm²"

                   # if self.v:
                   #     await self.plot_save_v(f"{folder}/{self.output_dir}/{file}", led, title)
                   # if self.c:
                   #     await self.plot_save_c(f"{folder}/{self.output_dir}/{file}", led, title)
                    # self.single_plot_paths.clear()
                    current_led_list.leds.append(led)

            if len(current_led_list.leds) == 0:
                return "no well formatted files found"

            first_led = current_led_list.leds[0]
            footer = f"{round(first_led.LED_Dim_x * 10 ** 4)} µm x {round(first_led.LED_Dim_y * 10 ** 4)} µm"

            # calc ax limits
            current_led_list.measurement_completed()
            self.limit_x_axis_voltage_end = max(current_led_list.voltage_array_mean)
            self.limit_x_axis_density_end = max(current_led_list.current_density_array_mean)
            op_idx = 0
            while current_led_list.op_power_array_mean[op_idx] == 0:
                op_idx = op_idx + 1
            self.limit_x_axis_density_begin = current_led_list.current_density_array_mean[op_idx+1]



            file = "output"
            file_footer = footer.replace(" ", "_")

            # outsourcing extension methods
            #single = Single(current_led_list, folder, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

            # plot the 4 summary plots
            #await single.plot_save_c_sum(f"{folder}/{self.output_dir}/{file_footer}_c_sum", "all LEDs " + footer, current_led_list)
            #await single.plot_save_c_avg(f"{folder}/{self.output_dir}/{file_footer}_c_avg", "arithmetic mean and standard deviation " + footer, current_led_list)
            #await single.plot_save_c_fit(f"{folder}/{self.output_dir}/{file_footer}_c_fit", "curve fitting " + footer)
            #await single.plot_save_sum_v(f"{folder}/{self.output_dir}/{file_footer}_v_sum", "all LEDs " + footer, current_led_list)
            #await single.plot_save_avg_v(f"{folder}/{self.output_dir}/{file_footer}_v_avg", "arithmetic mean and standard deviation " + footer, current_led_list)

            # output path and filename for summary pdf
            #pdf_summary_path = f"{folder}/{self.output_dir}/summary_{file_footer}.pdf"

            # create the actual summary pdf
            header = f'Measurement report {date_time}'
            #pdfc.PDF(header, footer).create_summary_pdf(self.summary_plot_paths, pdf_summary_path, f"Summary of {len(current_led_list.leds)} x {footer}",
           #                                             current_led_list)

            # create csv
            csv_path = f'{folder}/{self.output_dir}/_output.csv'
            current_led_list.create_csv(csv_path)

            self.list_of_measurements.append(current_led_list)

        # all measurements
        multi = Multi(self.filepath, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

        await multi.plot_save_c_avg(f"{syspath}_wpe_overview", "all sizes ", self.list_of_measurements)
        await multi.plot_allsizes_wpemax(f"{syspath}_wpe_max_all_sizes", "wpe max overview", self.list_of_measurements)

        return "finished"


    async def plot_save_c(self, file, led, title):
        array_x, array_y, array2_y = led.current_density_array[led.voltage_start_wpe_index:], \
                                     led.op_power_array[led.voltage_start_wpe_index:], \
                                     led.wpe_array[led.voltage_start_wpe_index:]
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
        fig.savefig(file)
        self.single_plot_paths.append(file)

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
        fig.savefig(file)
        self.single_plot_paths.append(file)

