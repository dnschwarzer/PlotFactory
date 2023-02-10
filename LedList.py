import numpy as np

import led_properties as led
import csv


class LedList:

    leds: led = []

    # data
    voltage_array = []
    current_array = []
    current_density_array = []
    wpe_array = []
    op_power_array = []

    # std
    voltage_array_std = []
    current_array_std = []
    current_density_array_std = []
    wpe_array_std = []
    op_power_array_std = []

    # means
    voltage_array_mean = []
    current_array_mean = []
    current_density_array_mean  = []
    wpe_array_mean  = []
    op_power_array_mean  = []

    # overview
    is_shorted_cnt = 0
    is_open_circuit_cnt = 0

    def __init__(self):
        self.leds = []

    def filter(self):
        tmp_list = []
        for pixel in self.leds:
            tmp_list.append(pixel.wpe_array)
            if pixel.is_shorted:
                self.is_shorted_cnt = self.is_shorted_cnt + 1
            if pixel.is_open_circuit:
                self.is_open_circuit_cnt = self.is_open_circuit_cnt + 1

        max_data_points = len(max(tmp_list, key=len))

        for pixel in self.leds:
            if len(pixel.wpe_array) != max_data_points:
                pixel.is_malfunctioning = True

    def measurement_completed(self):
        self.filter(self)

        # sort for LED no
        self.leds.sort(key=lambda x: x.led_no)

        for pixel in self.leds:
            if not pixel.is_malfunctioning:
                self.voltage_array.append(pixel.voltage_korr_array)
                self.current_array.append(pixel.current_soll_array)
                self.op_power_array.append(pixel.op_power_array)
                self.current_density_array.append(pixel.current_density_array)
                self.wpe_array.append(pixel.wpe_array)

        self.calc_std_err_mean(self)

    def calc_std_err_mean(self):
        data_points = len(self.leds[0].voltage_array)

        # tmp arrays
        tmp_voltage = []
        tmp_current = []
        tmp_density = []
        tmp_wpe = []
        tmp_op_power = []

        for point in range(0, data_points):
            for led in self.leds:
                tmp_voltage.append(led.voltage_korr_array[point])
                tmp_current.append(led.current_soll_array[point])
                tmp_density.append(led.current_density_array[point])
                tmp_wpe.append(led.wpe_array[point])
                tmp_op_power.append(led.op_power_array[point])

            # error
            self.voltage_array_std.append(np.std(tmp_voltage))
            self.current_array_std.append(np.std(tmp_current))
            self.current_density_array_std.append(np.std(tmp_density))
            self.wpe_array_std.append(np.std(tmp_wpe))
            self.op_power_array_std.append(np.std(tmp_op_power))

            # mean
            self.voltage_array_mean.append(np.mean(tmp_voltage))
            self.current_array_mean.append(np.mean(tmp_current))
            self.current_density_array_mean.append(np.mean(tmp_density))
            self.wpe_array_std_mean.append(np.mean(tmp_wpe))
            self.op_power_array_mean.append(np.mean(tmp_op_power))

            # clear tmp list
            tmp_voltage.clear()
            tmp_current.clear()
            tmp_density.clear()
            tmp_wpe.clear()
            tmp_op_power.clear()

    def create_csv(self, path):
        first_measurement = self.leds[0]
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n', delimiter=";")
            row = ["LED size x [um]", "LED size y [um]", "WPE max [%]", "I max [mA]", "J max [A per cm2]",
                   "Opt. Power [uW] at WPE max", "mnits at WPE max with FF", "WPE [%] at " + str(first_measurement.current_value * 10 ** 6) + "uA",
                   "Opt. Power [uW] at 20uA", "mnits at 20uA with FF",
                   " J [A per cm2]  at " + str(first_measurement.current_value * 10 ** 6) + "mA"]
            writer.writerow(row)
            for pixel in self.leds:
                row = [pixel.LED_Dim_x, pixel.LED_Dim_x, pixel.wpe_max, pixel.i_max * 10 ** 6, pixel.j_max,
                       pixel.op_power_max * 10 ** 6, pixel.nits_max_FF / 10 ** 6, pixel.wpe_current,
                       pixel.op_power_current * 10 ** 6, pixel.nits_current_FF / 10 ** 6, pixel.current_value / pixel.led_area]
                for j, r in enumerate(row):
                    row[j] = '{0:.2f}'.format(r).replace(".", ",")
                writer.writerow(row)  # str(a).replace(".", ","))
