import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import pdf_creator as pdfc
from pdf_creator import TableData
import led_properties



class Auswertung:

    output_dir = "Output"
    single_plot_paths = []
    summary_plot_paths = []
    voltage_array_sum = []
    current_array_sum = []
    op_power_array_sum_v = []
    current_density_array_sum = []
    wpe_array_sum = []
    op_power_array_sum_c = []
    summary_table_data = []
    summary_table_data_malfunc = []

    def __init__(self, filepath, c: bool, v: bool):
        self.filepath = filepath
        self.c = c
        self.v = v

    async def build(self) -> str:
        return await self.plot_files(self.filepath)

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    async def plot_save_c(self, file, array_x, array_y, array2_y, title):
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
        ax2.plot(array_x, array2_y * 100, 'b')
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
        plt.xlim([10**2, 10**4])

        data_points = len(current_density)
        for idx in range(0, data_points):
            ax.plot(current_density[idx], op_power[idx], "k")

        ax.set_xscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_yscale('log')
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

    async def plot_save_v(self, file, array_x, array_y, array2_y, title):

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
        plt.xlim([10**2, 10**4])
        #plt.xlim([0,4])

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
        ax.set_yscale('log')
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)
        ax2 = ax.twinx()
        ax2.errorbar(voltages, op_power, op_power_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(voltages, op_power, s=4, linewidths=0.1, color='blue')

        # ax2.plot(voltages, op_power, 'b')

        ax2.grid(True)

        ax2.set_xscale('log')
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

        #plt.ylim([5 * 10**-8, 10**-2])
        ax.errorbar(voltages, currents, currents_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(voltages, currents, s=4, linewidths=0.1, color='black')
        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.set_yscale('log')

        ax.grid(True)
        ax2 = ax.twinx()
        ax2.errorbar(voltages, opPower, opPower_std,
                     fmt=',', linewidth=0.5, color='blue',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(voltages, opPower, s=4,  linewidths=0.1, color='blue')
        ax2.grid(True)
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

    async def plot_save_sum_v(self, file, array_x, array_y, array2_y, title):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title)
        #plt.ylim([10**-7, 10**-4])

        for x in range(0, len(array_x)):
            ax.plot(array_x[x], array_y[x], "k")

        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.set_yscale('log')
        #plt.xlim([0,4])

        ax.grid(True)
        ax2 = ax.twinx()
        for x in range(0, len(array_x)):
            ax2.plot(array_x[x], array2_y[x], 'b')

        ax2.grid(True)
        ax2.set_yscale('log')
        ax2.set_xlabel("Voltage [V]")
        ax2.set_ylabel("Opt. Power [W]")
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        file = file.replace(".csv", "_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{self.output_dir}/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_files(self, filepath) -> str:
        syspath = filepath
        if syspath == "" or syspath == " ":
            return "no path provided"

        if not os.path.exists(syspath):
            return "provided path doesnt exist"

        if not os.path.exists(syspath + f"\\{self.output_dir}"):
            os.makedirs(syspath + f"\\{self.output_dir}")
        lumefficency_blue = 42
        CurrentValue = 20 * 10 ** (-6)
        OpPowerLimit = 10 ** -7
        OpenCircuitLimit = 10 ** -6
        Voltage_Start_WPE = 2

        # wat is dis

        IVL_NA = 0.91
        IVL_WPE_Collection = IVL_NA ** 2

        OpPower_WPE_Max = []
        nits_WPE_Max_List = []
        WPE_Current_List = []
        OpPower_Current = []
        nits_Current_List = []
        I_Max_List = []
        LED_Area_List = []
        LED_Dim_List = []
        i_3_3v = []
        op_power_3_3v = []
        WPE_Max_List = []
        J_Max_List = []


        file_cnt = 0
        for file in os.listdir(syspath):
            if file.endswith(".csv"):
                file_cnt = file_cnt + 1
                file_name = file.title().replace(".Csv", "")
                date_time = file_name.split("____")[0].replace("_", "-")
                measure_meta = file_name.split("____")[1]
                led_no = int(measure_meta.split("_")[0].replace("Q", ""))
                led_id = int(measure_meta.split("_")[1].replace("Id", ""))
                led_area = float(measure_meta.split("_")[2].replace("D", ""))

                led = led_properties.LED(led_no, led_area, led_id)
                LED_Dim_x = led.LED_Dim_x
                LED_Dim_y = led.LED_Dim_y
                LED_Dim_List.append((LED_Dim_x, LED_Dim_y))
                LED_Area = LED_Dim_x * LED_Dim_y * 10 ** (-8)  # cm²
                LED_Area_List.append(LED_Area)
                with open(f'{syspath}/{file}', 'r') as f:
                    next(f)
                    u_mess_li = []
                    u_korr_li = []
                    i_soll_li = []
                    i_mess_li = []
                    op_power_li = []
                    current_density_li = []
                    measure_time_lo = []
                    reader = csv.reader(f, delimiter=";")

                    cnt = 2
                    for row in reader:
                        u_mess = float(row[0])
                        u_korr = float(row[1])
                        i_soll = float(row[2])
                        i_mess = float(row[3])
                        opt_power = float(row[4])
                        current_density = float(row[5])
                        measure_time = float(row[6])
                        if opt_power == float('inf'):
                            opt_power = 0
                            print(f"inf at Q:{led_no}_ID{led_id}, row : {cnt}")
                        cnt = cnt + 1

                        u_mess_li.append(u_mess)
                        u_korr_li.append(u_korr)
                        i_soll_li.append(i_soll)
                        i_mess_li.append(i_mess)


                        # if(opt_power > 7*10E-10;100*opt_power/(volt*current);0)
                        if opt_power > 7*10**-10:
                            #opt_power = 100 * opt_power/(u_korr * i_mess)
                            opt_power = opt_power
                        else:
                            opt_power = 0

                        op_power_li.append(opt_power)
                        current_density_li.append(current_density)
                        measure_time_lo.append(measure_time)
                Voltage_Array = np.asarray(u_mess_li)
                Current_Soll_Array = np.asarray(i_soll_li)
                Current_Mess_Array = np.asarray(i_mess_li)
                #curr = max(abs((Current_Soll_Array - Current_Mess_Array) / Current_Soll_Array * 100))
                #print(curr)
                CurrentDensity_Array = np.asarray(current_density_li)
                opPower_Array = np.asarray(op_power_li)

                # WPE = P_opt / P_el
                WPE_min_Array = 100 * opPower_Array / (Voltage_Array * Current_Mess_Array)

                Last_opValue_Value = opPower_Array[len(opPower_Array) - 1]
                Last_Current_Value = Current_Soll_Array[len(Current_Soll_Array) - 1]

                if (Last_opValue_Value > OpPowerLimit):
                    IsOpenCircuit = False
                    IsShorted = False
                elif (Last_Current_Value < OpenCircuitLimit):
                    led.is_open_circuit = True
                    IsOpenCircuit = True
                    IsShorted = False
                else:
                    led.is_shorted = True
                    IsOpenCircuit = False
                    IsShorted = True

                Voltage_Start_WPE_Index = self.find_nearest(Voltage_Array, value=Voltage_Start_WPE)
                WPE_Min_Max = max(WPE_min_Array[Voltage_Start_WPE_Index:])
                WPE_Max_Index = self.find_nearest(WPE_min_Array, value=WPE_Min_Max)
                CurrentValue_Index = self.find_nearest(Current_Soll_Array, value=CurrentValue)
                opPower_current = 0
                nits_current = 0
                opPower_max = 0
                nits_max = 0
                nits_current_FF = 0
                nits_max_FF = 0

                if (IsOpenCircuit or IsShorted):
                    WPE_min_At_CurrentIndex = 0
                    WPE_Min_Max = 0
                else:
                    WPE_min_At_CurrentIndex = WPE_min_Array[CurrentValue_Index]
                    opPower_current = opPower_Array[CurrentValue_Index]
                    # warum * 10 ^-12
                    Area = LED_Dim_x * LED_Dim_y * 10 ** -12
                    FF = LED_Dim_x * LED_Dim_y / (18.5 * 18.5)
                    nits_current = opPower_current * lumefficency_blue / (Area * np.pi)
                    nits_current_FF = nits_current * FF
                    opPower_max = opPower_Array[WPE_Max_Index]
                    nits_max = opPower_max * lumefficency_blue / (Area * np.pi)
                    nits_max_FF = nits_max * FF
                WPE_Current_List.append(WPE_min_At_CurrentIndex / IVL_WPE_Collection)
                OpPower_Current.append(opPower_current)
                nits_Current_List.append(nits_current_FF)

                WPE_Array = abs(WPE_min_Array / IVL_WPE_Collection)
                WPE_Max = WPE_Min_Max / IVL_WPE_Collection
                WPE_Max_List.append(WPE_Max)
                I_Max = Current_Soll_Array[WPE_Max_Index]
                I_Max_List.append(I_Max)

                # J = I / A
                J_Max = Current_Soll_Array[WPE_Max_Index] / LED_Area
                J_Max_List.append(J_Max)
                OpPower_WPE_Max.append(opPower_max)
                nits_WPE_Max_List.append(nits_max_FF)
                # print(file, Voltage_Array[CurrentValue_Index], Current_Soll_Array[CurrentValue_Index], WPE_min_At_CurrentIndex, IsOpenCircuit, IsShorted)
                title = f"Q{led.led_no} ID{led.led_id} : " + str(LED_Dim_x) + " µm x " + str(LED_Dim_y) + " µm, WPE_max = " + str(
                    WPE_Max * 100) + " %, J_Max = " + str(CurrentDensity_Array[CurrentValue_Index]) + "A/cm²"

                if self.v:
                    await self.plot_save_v(f"{syspath}/{file}", Voltage_Array, Current_Soll_Array, opPower_Array, title)
                if self.c:
                    await self.plot_save_c(f"{syspath}/{file}", CurrentDensity_Array[Voltage_Start_WPE_Index:], opPower_Array[Voltage_Start_WPE_Index:], WPE_Array[Voltage_Start_WPE_Index:], title)

                #if not IsOpenCircuit and not IsShorted:
                self.voltage_array_sum.append(Voltage_Array)
                self.current_array_sum.append(Current_Soll_Array)
                self.op_power_array_sum_v.append(opPower_Array)
                self.wpe_array_sum.append(WPE_Array)
                self.current_density_array_sum.append(CurrentDensity_Array)
                self.op_power_array_sum_c.append(opPower_Array)

                #data for table
                voltage_3_3 = self.find_nearest(Voltage_Array, value=2.3) # 2.3 weil messungen nur bis 2.7v
                i_3_3v = Current_Soll_Array[voltage_3_3]
                op_power_3_3v = opPower_Array[voltage_3_3]
                table_entry = TableData(led.led_no, led.led_id, J_Max, WPE_Max, i_3_3v, op_power_3_3v, IsShorted, IsOpenCircuit)
                self.summary_table_data.append(table_entry)
                self.single_plot_paths.clear()

        # delete malfunctioning leds from arrays so plots do not get messed up
        malfunc = []
        j = 0
        for i in range(len(self.wpe_array_sum)):
            if self.wpe_array_sum[i][0] > 1 or self.summary_table_data[i].is_open:
                self.summary_table_data[i].is_open = True
                self.summary_table_data_malfunc.append(self.summary_table_data[i])
                malfunc.append(i-j)
                j = j+1
            if max(self.voltage_array_sum[i]) > 4 or self.summary_table_data[i].is_shorted:
                self.summary_table_data[i].is_shorted = True
                self.summary_table_data_malfunc.append(self.summary_table_data[i])
                malfunc.append(i-j)
                j = j+1

        for mal in malfunc:
            del self.current_density_array_sum[mal]
            del self.op_power_array_sum_c[mal]
            del self.voltage_array_sum[mal]
            del self.wpe_array_sum[mal]
            del self.op_power_array_sum_v[mal]
            del self.current_array_sum[mal]

        # plot the 4 summary plots
        await self.plot_save_c_sum(f"{syspath}/{file}_c_sum", self.current_density_array_sum, self.op_power_array_sum_c, self.wpe_array_sum, "all LEDs")
        await self.plot_save_c_avg(f"{syspath}/{file}_c_avg", self.current_density_array_sum, self.op_power_array_sum_c, self.wpe_array_sum, "arithmetic mean and standard deviation")
        await self.plot_save_sum_v(f"{syspath}/{file}_v_sum", self.voltage_array_sum, self.current_array_sum, self.op_power_array_sum_v, "all LEDs")
        await self.plot_save_avg_v(f"{syspath}/{file}_v_avg", self.voltage_array_sum, self.current_array_sum, self.op_power_array_sum_v, "arithmetic mean and standard deviation")

        # sort summary table for led no
        self.summary_table_data.sort(key=lambda x: x.no)

        # output path and filename for summary pdf
        pdf_summary_path = f"{self.filepath}/{self.output_dir}/summary.pdf"

        # create the actual summary pdf
        pdfc.PDF(f'Measurement report {date_time}').create_summary_pdf(self.summary_plot_paths, pdf_summary_path, "summary", self.summary_table_data, self.summary_table_data_malfunc)

        with open(f'{syspath}/{self.output_dir}/_output.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n', delimiter=";")
            row = ["LED size x [um]", "LED size y [um]", "WPE max [%]", "I max [mA]", "J max [A per cm2]",
                   "Opt. Power [uW] at WPE max", "mnits at WPE max with FF", "WPE [%] at " + str(CurrentValue * 10 ** 6) + "uA",
                   "Opt. Power [uW] at 20uA", "mnits at 20uA with FF",
                   " J [A per cm2]  at " + str(CurrentValue * 10 ** 6) + "mA"]
            writer.writerow(row)
            for i, a in enumerate(WPE_Max_List):
                row = [LED_Dim_List[i][0], LED_Dim_List[i][1], WPE_Max_List[i] * 100, I_Max_List[i] * 10 ** 6, J_Max_List[i],
                       OpPower_WPE_Max[i] * 10 ** 6, nits_WPE_Max_List[i] / 10 ** 6, WPE_Current_List[i] * 100,
                       OpPower_Current[i] * 10 ** 6, nits_Current_List[i] / 10 ** 6, CurrentValue / LED_Area_List[i]]
                for j, r in enumerate(row):
                    row[j] = '{0:.2f}'.format(r).replace(".", ",")
                writer.writerow(row)  # str(a).replace(".", ","))
        return "finished"





