import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import pdf_creator as pdfc


class Auswertung:

    output_dir = "Output"
    file_paths = []
    voltage_array_dim_2 = []
    current_array_dim_2 = []
    op_power_array_dim_2 = []


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
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title(title)
        ax.plot(array_x, array_y, "k")
        ax.set_xscale('log')
        ax.set_xlabel("Current [A/cm²]")
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
        self.file_paths.append(path)


    async def plot_save_v(self, file, array_x, array_y, array2_y, title):

        fig, ax = plt.subplots(figsize=(9, 6))
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
        self.file_paths.append(path)


    #self.plot_save_v(f"{syspath}/{file}", Voltage_Array, Current_Array, opPower_Array, title)
    async def plot_save_avg_v(self, file, array_x, array_y, array2_y, title):

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title(title)


        # array_x[voltage][arrayNo] =
        currents = []
        currents_std = []
        voltages = []
        voltages_std = []
        opPower = []
        opPower_std = []
        average_c = []
        average_v = []
        average_p = []

        for idx in range(0, len(array_y[0])):
            for curr in range(0, len(array_y)):
                average_c.append(array_y[curr][idx])
            currents.append(np.mean(average_c))
            currents_std.append(np.std(average_c))
            average_c.clear()

        for idx in range(0, len(array_x[0])):
            for vol in range(0, len(array_x)):
                average_v.append(array_x[vol][idx])
            voltages.append(np.mean(average_v))
            voltages_std.append(np.std(average_v))
            average_v.clear()

        for idx in range(0, len(array2_y[0])):
            for o_pow in range(0, len(array2_y)):
                average_p.append(array2_y[o_pow][idx])
            opPower.append(np.mean(average_p))
            opPower_std.append(np.std(average_p))
            average_p.clear()

        ax.errorbar(voltages, currents, currents_std, fmt='-o',  color='black')
       # ax.plot(voltages, currents, "k")

        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.set_yscale('log')

        ax.grid(True)
        ax2 = ax.twinx()
        ax2.errorbar(voltages, opPower, opPower_std, fmt='-o', color='blue')
        ax2.plot(voltages, opPower, 'b')

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
        self.file_paths.append(path)

    async def plot_save_sum_v(self, file, array_x, array_y, array2_y, title):

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title(title)

        for x in range(0, len(array_x)):
            ax.plot(array_x[x], array_y[x], "k")

        ax.set_xlabel("Voltage [V]")
        ax.set_ylabel("Current [A]")
        ax.set_yscale('log')

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
        self.file_paths.append(path)

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
        IVL_NA = 0.91
        IVL_WPE_Collection = IVL_NA ** 2

        WPE_Max_List = []
        OpPower_WPE_Max = []
        nits_WPE_Max_List = []
        WPE_Current_List = []
        OpPower_Current = []
        nits_Current_List = []
        I_Max_List = []
        J_Max_List = []
        LED_Area_List = []
        LED_Dim_List = []

        file_cnt = 0
        for file in os.listdir(syspath):
            if file.endswith(".csv"):
                file_cnt = file_cnt + 1
                index_start = file.find("_", file.find("_", file.find("_") + 1) + 1)
                index_end = file.find(".")
                h_string = file[index_start + 1:index_end].replace("um", "").replace("x", "")
                LED_Dim_x = h_string[:h_string.find("_")].replace(",", ".")
                LED_Dim_y = h_string[h_string.find("_") + 1:].replace(",", ".")
                LED_Dim_x = float(LED_Dim_x)
                LED_Dim_y = float(LED_Dim_y)
                LED_Dim_List.append((LED_Dim_x, LED_Dim_y))
                LED_Area = LED_Dim_x * LED_Dim_y * 10 ** (-8)  # cm²
                LED_Area_List.append(LED_Area)
                with open(f'{syspath}/{file}', 'r') as f:
                    Voltage_List = []
                    Current_List = []
                    opPower_List = []
                    reader = csv.reader(f, delimiter=";")
                    for row in reader:
                        Voltage_List.append(float(row[0]))
                        Current_List.append(float(row[1]))
                        opPower_List.append(float(row[2]))
                Voltage_Array = np.asarray(Voltage_List)
                Current_Array = np.asarray(Current_List)
                CurrentDensity_Array = Current_Array / (LED_Area)
                opPower_Array = np.asarray(opPower_List)
                WPE_min_Array = opPower_Array / (Voltage_Array * Current_Array)
                Last_opValue_Value = opPower_Array[len(opPower_Array) - 1]
                Last_Current_Value = Current_Array[len(Current_Array) - 1]

                if (Last_opValue_Value > OpPowerLimit):
                    IsOpenCircuit = False
                    IsShorted = False
                elif (Last_Current_Value < OpenCircuitLimit):
                    IsOpenCircuit = True
                    IsShorted = False
                else:
                    IsOpenCircuit = False
                    IsShorted = True
                Voltage_Start_WPE_Index = self.find_nearest(Voltage_Array, value=Voltage_Start_WPE)
                WPE_Min_Max = max(WPE_min_Array[Voltage_Start_WPE_Index:])
                WPE_Max_Index = self.find_nearest(WPE_min_Array, value=WPE_Min_Max)
                CurrentValue_Index = self.find_nearest(Current_Array, value=CurrentValue)
                opPower_current = 0
                nits_current = 0
                opPower_max = 0
                nits_max = 0
                if (IsOpenCircuit or IsShorted):
                    WPE_min_At_CurrentIndex = 0
                    WPE_Min_Max = 0
                else:
                    WPE_min_At_CurrentIndex = WPE_min_Array[CurrentValue_Index]
                    opPower_current = opPower_Array[CurrentValue_Index]
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

                WPE_Array = WPE_min_Array / IVL_WPE_Collection
                WPE_Max = WPE_Min_Max / IVL_WPE_Collection
                WPE_Max_List.append(WPE_Max)
                I_Max_List.append(Current_Array[WPE_Max_Index])
                J_Max_List.append(Current_Array[WPE_Max_Index] / LED_Area)
                OpPower_WPE_Max.append(opPower_max)
                nits_WPE_Max_List.append(nits_max_FF)
                # print(file, Voltage_Array[CurrentValue_Index], Current_Array[CurrentValue_Index], WPE_min_At_CurrentIndex, IsOpenCircuit, IsShorted)
                title = str(LED_Dim_x) + " µm x " + str(LED_Dim_y) + " µm, WPE_max = " + str(
                    WPE_Max * 100) + " %, J_Max = " + str(CurrentDensity_Array[CurrentValue_Index]) + "A/cm²"

                if self.v:
                    await self.plot_save_v(f"{syspath}/{file}", Voltage_Array, Current_Array, opPower_Array, title)
                if self.c:
                    await self.plot_save_c(f"{syspath}/{file}", CurrentDensity_Array[Voltage_Start_WPE_Index:], opPower_Array[Voltage_Start_WPE_Index:], WPE_Array[Voltage_Start_WPE_Index:], title)

                if not IsOpenCircuit and not IsShorted:
                    self.voltage_array_dim_2.append(Voltage_Array)
                    self.current_array_dim_2.append(Current_Array)
                    self.op_power_array_dim_2.append(opPower_Array)

                file_name_extracted = file.split(".")[0]
                pdf_file_path = f"{self.filepath}/{self.output_dir}/{file_name_extracted}.pdf"
                pdfc.create_pdf(self.file_paths, pdf_file_path, file_name_extracted)
                self.file_paths.clear()

        #await self.plot_save_sum_v(f"{syspath}/{file}", self.voltage_array_dim_2, self.current_array_dim_2, self.op_power_array_dim_2, title)
        await self.plot_save_avg_v(f"{syspath}/{file}", self.voltage_array_dim_2, self.current_array_dim_2, self.op_power_array_dim_2, title)

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
