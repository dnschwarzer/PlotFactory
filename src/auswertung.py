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
import auswertung_helper as static_m
import matplotlib.pyplot as plt
import warnings


debug_mode = False

if not debug_mode:
    warnings.filterwarnings('ignore')

def print_debug(text):
    pass

if debug_mode:
    def print_debug(text):
        print(text)    

def print_summary(current_led_list):
    print('\033[92m' + f"{current_led_list.leds[0].LED_Dim_x * 10 ** 4} µm² {current_led_list.geometric} R 1_{current_led_list.ratio_str} {len(current_led_list.leds)} LEDs processed: " + '\033[0m')
    print(f"wpe max of mean: {current_led_list.wpe_mean_max} j at wpe max: {max(current_led_list.j_at_wpe_max)}")
    # print summary of malfunctions in current_led_list
    malfuncs = 0
    for led in current_led_list.leds:
        if led.is_malfunctioning:
            malfuncs = malfuncs + 1
    print(f"{malfuncs} out of {len(current_led_list.leds)} LEDs are malfunctioning / not counted")
    print(f"most commong datapoint length: {current_led_list.max_data_points} per LED")
    print("")


def format_e(n):
    a = '%E' % n
    b = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
    return f"{b:.{4}}"

# hardcoded values, no logic behind it
def get_ratio(size):
    if size == "3":
        return 3
    elif size == "6":
        return 5
    elif size == "9":
        return 10
    elif size == "18":
        return 20

    #print("size: " + size)


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

    def __init__(self, filepath, do_pixel_plot: bool, do_array_plot: bool, do_summary_plot: bool, do_correction: bool):
        self.filepath = filepath
        self.do_pixel_plot = do_pixel_plot
        self.do_array_plot = do_array_plot
        self.do_summary_plot = do_summary_plot
        self.fontsize = 25
        self.do_correction = do_correction

    async def build(self) -> str:
        return await self.plot(self.filepath)

    async def plot(self, filepath) -> str:
        syspath = filepath
        if syspath == "" or syspath == " ":
            return "no path provided"

        if not os.path.exists(syspath):
            return "provided path doesnt exist"

        subfolders = [f.path for f in os.scandir(syspath) if f.is_dir()]

        correction_start = 1 * 10 ** -1
        correction = 1.3 * 10 ** -1
        idxs = 0
        for corr in range(0, 1):
            correction += 0.01

            correction = round(correction, 3)
            if not self.do_correction:
                correction = 0

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
                        date = file_name_split[0].split("__")[0].replace("_", "-")
                        measure_meta = file_name_split[1].lower()

                        # assignments
                        measure_meta_split = measure_meta.split("_")
                        correction_ratio = 1.0

                        if len(measure_meta_split) == 3:
                            led_no = (measure_meta_split[0].replace("q", ""))
                            current_led_list.color = "green" if led_no == "unknown" else "blue"

                            led_id = int(measure_meta_split[1].replace("id", ""))
                            edge_length = float(measure_meta_split[2].replace("d", ""))
                            correction_ratio = (float(edge_length) - float(correction)) / float(edge_length)
                            edge_length = float(edge_length) - float(correction)


                            current_led_list.edge_length = edge_length
                            led_area = edge_length * edge_length
                            led = led_properties.LED(led_no, led_area, led_id, date_time)


                        elif len(measure_meta_split) == 4:
                            led_no = int(measure_meta_split[1])
                            led_id = int(measure_meta_split[2].replace("id", ""))

                            has_aspect_ratio = True if measure_meta_split[0].find("r") != -1 else False
                            ratio = float(1)

                            # die Rechtecke sind: 1:3 - 1x1.73µm², 1:5 - 1x2.24µm², 1:10 - 1x 3.16µm², 1:20 - 1x4.47µm²
                            if has_aspect_ratio:
                                size = measure_meta_split[0].replace("r1", "").replace(" ", "")
                                ratio = float(size) if int(measure_meta_split[3].replace("d", "")) != 1 else float(get_ratio(size))
                                current_led_list.geometric = "rectangle"
                            else:
                                geometry = measure_meta_split[0]
                                if geometry.find("q") != -1:
                                    size = measure_meta_split[0].replace("q", "").replace(" ", "")
                                    current_led_list.geometric = "quadrat"
                                elif geometry.find("d") != -1:
                                    size = measure_meta_split[0].replace("d", "").replace(" ", "")
                                    current_led_list.geometric = "diamond"
                                elif geometry.find("c") != -1:
                                    size = measure_meta_split[0].replace("c", "").replace(" ", "")
                                    current_led_list.geometric = "circle"
                                elif geometry.find("e") != -1:
                                    size = measure_meta_split[0].replace("e", "").replace(" ", "")
                                    current_led_list.geometric = "ellipse"  

                            edge_length = float(measure_meta_split[3].replace("d", ""))
                            correction_ratio = (float(edge_length) - float(correction)) / float(edge_length)
                            edge_length = float(edge_length) - float(correction)
                            current_led_list.edge_length = edge_length
                            current_led_list.ratio = ratio
                            current_led_list.ratio_str =  f"1:{int(ratio)}"
                            pixel_size_x = np.sqrt(1/ratio)*edge_length
                            pixel_size_x = 1 if pixel_size_x < 1 else pixel_size_x
                            pixel_size_y = edge_length * np.sqrt(ratio)
                            led_area = round(pixel_size_x * pixel_size_y)

                            led = led_properties.LED(led_no, led_area, led_id, date_time)
                        else:
                            continue

                        correction_ratio *= correction_ratio
                        current_led_list.area_correction = correction

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

                                try:
                                    u_mess = float(row[0]) * float(correction_ratio)
                                    u_korr = float(row[1]) * float(correction_ratio)
                                    i_soll = float(row[2]) * float(correction_ratio)
                                    opt_power = float(row[3])
                                except ValueError:
                                    led.is_malfunctioning = True
                                    continue

                                current_density = i_soll / (led_area * 10 ** -8)

                                # filter opt_power noise
                                # if(opt_power > 7*10E-10;100*opt_power/(volt*current);0)
                                if opt_power < 3*10**-8 or cnt < 10:
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

                        if len(i_soll_li) <= self.minimum_datapoints:
                            continue

                        # add data to led object and calculate other properties
                        led.add_data(u_mess_li, u_korr_li, i_soll_li, current_density_li, op_power_li)
                        current_led_list.leds.append(led)

                        title = f"Q{led.led_no} ID{led.led_id} : " + str(round(led.LED_Dim_y * 10 ** 4)) \
                                + " µm x " + str(round(led.LED_Dim_y * 10 ** 4)) + " µm, WPE_max = " + f"{float(led.wpe_max):.{3}} %, J_Max = {float(led.j_max):.{6}} A/cm²"

                        if self.do_pixel_plot:
                            await self.plot_save_v(f"{folder}/{self.output_dir}/{file}", led, title)
                            await self.plot_save_c(f"{folder}/{self.output_dir}/{file}", led, title)
                            await self.plot_save_e(f"{folder}/{self.output_dir}/{file}", led, title)
                            await self.plot_save_f(f"{folder}/{self.output_dir}/{file}", led, title)
                            await self.plot_save_iqe(f"{folder}/{self.output_dir}/{file}", led, title)
                            self.single_plot_paths.clear()

                if len(current_led_list.leds) == 0:
                    print('\033[91m' + 'no well formatted files found!' + '\033[0m')
                    return "no well formatted files found"

                first_led = current_led_list.leds[0]
                footer = f"{round(current_led_list.edge_length, 2)}µm {current_led_list.geometric} R 1_{round(current_led_list.ratio, 2)}"

                #footer = f"{round(first_led.LED_Dim_x * 10 ** 4), 2}x{round(first_led.LED_Dim_y * 10 ** 4), 2} µm"
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

                # print summary to console
                print_summary(current_led_list)

                



                if self.do_array_plot:
                    # outsourcing extension methods
                    single = Single(current_led_list, folder, self.limit_x_axis_density_begin, self.limit_x_axis_density_end, self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end, self.summary_plot_paths)

                    # plot the 4 summary plots
                    await single.plot_save_c_sum(f"{folder}/{self.output_dir}/{file_footer}_c_sum", "all LEDs " + footer, current_led_list)
                    await single.plot_save_c_avg(f"{folder}/{self.output_dir}/{file_footer}_c_avg", "arithmetic mean and standard deviation " + footer, current_led_list)
                   # await single.plot_save_c_fit(f"{folder}/{self.output_dir}/{file_footer}_c_fit", "curve fitting " + footer)
                    await single.plot_save_sum_v(f"{folder}/{self.output_dir}/{file_footer}_v_sum", "all LEDs " + footer, current_led_list)
                    await single.plot_save_avg_v(f"{folder}/{self.output_dir}/{file_footer}_v_avg",  footer, current_led_list)
                    await single.plot_save_iqe(f"{folder}/{self.output_dir}/{file_footer}_iqe", "IQE " + footer, current_led_list)

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
                iqe_wpe_paths = [f'{syspath}/_size_iqe_wpe_{correction}.csv']
                multi.create_overview_csv(iqe_wpe_paths, self.list_of_measurements)

                await multi.plot_allsizes_wpemax(f"{syspath}_wpe_max_all_sizes", "wpe max overview", self.list_of_measurements)
                await multi.plot_allsizes_wpemax(f"{syspath}_wpe_max_all_sizes", "wpe max overview", self.list_of_measurements)
                await multi.plot_save_wpe_dens(f"{syspath}_wpe_dens_optp_all_sizes", "wpe all sizes", self.list_of_measurements)
                await multi.plot_allsizes_wpemax_aspect_ratio(f"{syspath}_wpe_max_aspect_ratio", "wpe max / aspect ratio", self.list_of_measurements)
                #await multi.plot_allsizes_wpe_wpemax_normalized(f"{syspath}_wpe_max_all_sizes_normalized", "wpe max overview", self.list_of_measurements)
                #await multi.plot_save_c_avg(f"{syspath}_wpe_overview", "overview", self.list_of_measurements)
                await multi.plot_allsizes_iqemax(f"{syspath}_iqe_overview", "overview", self.list_of_measurements)


                csv_paths = [f'{syspath}/_opt_dens.csv', f'{syspath}/_wpe_dens.csv']


                multi.create_csv(csv_paths, self.list_of_measurements)

            self.list_of_measurements.clear()
            self.summary_plot_paths.clear()
            self.single_plot_paths.clear()

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
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax.set_yscale('log')
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.grid(which='major', linestyle='-')
        ax.grid(which='minor', linestyle='--')
        ax.grid(True)
        static_m.scalar_formatter(ax)
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
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
        ax.set_xlabel("Voltage [V]", fontsize=self.fontsize)
        ax.set_ylabel("Current [A]", fontsize=self.fontsize)
        ax.grid(True)
        ax2 = ax.twinx()
        ax2.plot(array_x, array2_y, 'b')
        ax2.set_yscale('log')
        ax2.set_xlabel("Voltage [V]", fontsize=self.fontsize)
        ax2.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
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

        idx_wpe_max = led.wpe_array.argmax(axis=0)
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
        ax.set_xlabel("Current [A]", fontsize=self.fontsize)
        ax.set_ylabel("EQE", fontsize=self.fontsize)
        ax.grid(True)

        file = file.replace(".csv", "_e.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

    async def plot_save_iqe(self, file, led, title):
       # array_x, array_y = led.j_array, led.eqe_array
        array_x, array_y = led.j_array, led.eqe_array
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
        static_m.format_plot(plt, title, ax, self.fontsize)

        if len(array_x) > 0:

            end_idx = static_m.find_nearest(array_x,4)
            x = array_x[:end_idx]
            y = array_y[:end_idx]

            if not len(x) <= 0 and np.isfinite(x).all() and np.isfinite(y).all():
                # more x vals
                xfine = np.linspace(array_x[0], array_x[-1], 100)
                y_fitted = led.q_func(xfine, led.q)
                # print(f"LED: {led.led_no}  Q {popt[0]} pcov:{pcov[0]}")
                ax.scatter(xfine, y_fitted, c='green')

        static_m.scalar_formatter(ax)

        ax.plot(array_x, array_y, "k")
        ax.plot(array_x2, array_y2, "blue")
        ax.set_xlabel(f"sqrt(P) + 1/sqrt(P) | fit param: x0:{x[0]}, x_end:{x[-1]}, Q={float(led.q):.{6}}  covar={led.q_cov}, IQE_max = {float((led.q/(led.q+2))*10**2):.{3}}%", fontsize=self.fontsize-10)
        ax.set_ylabel("EQE_max / EQE", fontsize=self.fontsize)
        ax.grid(True)

        file = file.replace(".csv", "_f.png")
        fig.savefig(file)
        self.single_plot_paths.append(file)

