import numpy as np
import led_properties as led
import csv
from collections import Counter


class LedList:

    def __init__(self):
        self.leds = []
        self.area_correction = 0
        self.led_area_array = []
        self.area = 0
        self.edge_length = 0
        self.ratio = 1
        self.color = "blue"
        self.geometric = "square"

        # data
        self.voltage_array = []
        self.current_array = []
        self.current_density_array = []
        self.wpe_array = []
        self.eqe_array = []
        self.j_array = []
        self.op_power_array = []

        # std
        self.voltage_array_std = []
        self.current_array_std = []
        self.current_density_array_std = []
        self.wpe_array_std = []
        self.eqe_array_std = []
        self.op_power_array_std = []
        self.j_array_std = []

        # means
        self.voltage_array_mean = []
        self.current_array_mean = []
        self.current_density_array_mean = []
        self.wpe_array_mean = []
        self.eqe_array_mean = []
        self.op_power_array_mean = []
        self.j_array_mean = []

        # overview
        self.is_shorted_cnt = 0
        self.is_open_circuit_cnt = 0
        self.idx_wpe_max = 0
        self.wpe_mean_max = 0
        self.wpe_abs_max = 0
        self.iqe_max_mean = 0
        self.j_at_wpe_max = []
        self.j_at_wpe_max_mean = 0
        self.j_at_wpe_max_std = 0

        # helper fields
        self.max_data_points = 0

    def filter(self):
        tmp_list = []
        for pixel in self.leds:
            tmp_list.append(pixel.wpe_array)

        count = Counter()
        for led in self.leds:
            if len(led.wpe_array) >= 30:
                count[len(led.current_soll_array)] += 1

        # Ermitteln der am häufigsten auftretenden Subsublistenlängen
        most_common_lengths = sorted(count.items(), key=lambda x: (-x[1], -x[0]))

        (length, occ) = most_common_lengths[0]
        self.max_data_points = length

        # wenn nicht alle arrays gleiche länge : entferne
        mal = 0
        for pixel in self.leds:
            if len(pixel.wpe_array) != self.max_data_points:
                pixel.is_malfunctioning = True
                pixel.is_open_circuit = True
            if max(pixel.wpe_array) > 100 or round(np.mean(pixel.wpe_array)) == 0:
                pixel.is_malfunctioning = True
                pixel.is_open_circuit = True
            if pixel.is_shorted:
                self.is_shorted_cnt = self.is_shorted_cnt + 1
            if pixel.is_open_circuit:
                self.is_open_circuit_cnt = self.is_open_circuit_cnt + 1
            if pixel.is_malfunctioning:
                mal = mal + 1


       # print(f"{len(self.leds) -mal}:{len(self.leds)} Pixel used")

    def measurement_completed(self):
        self.filter()

        # sort for LED no
        self.leds.sort(key=lambda x: x.led_no)
        self.area = self.leds[0].LED_Dim_x * self.leds[0].LED_Dim_y if len(self.leds) > 0 else 0

        for pixel in self.leds:
            if not pixel.is_malfunctioning:
                self.voltage_array.append(pixel.voltage_korr_array)
                self.led_area_array.append(pixel.led_area)
                self.current_array.append(pixel.current_soll_array)
                self.op_power_array.append(pixel.op_power_array)
                self.current_density_array.append(pixel.current_density_array)
                self.wpe_array.append(pixel.wpe_array)
                self.eqe_array.append(pixel.eqe_array)
                self.j_at_wpe_max.append(pixel.j_at_wpe_max)
                self.j_array.append(pixel.j_array)

        self.calc_std_err_mean()

    def calc_std_err_mean(self):
        data_points = self.max_data_points

        # tmp arrays
        tmp_voltage = []
        tmp_current = []
        tmp_density = []
        tmp_wpe = []
        tmp_eqe = []
        tmp_op_power = []
        tmp_j = []
        tmp_iqe_max = []

        count = 0
        for point in range(0, data_points):
            for led in self.leds:
                # skip malfunctioning leds or corrupted measurements
                if led.is_malfunctioning:
                    continue
                tmp_voltage.append(led.voltage_korr_array[point])
                tmp_current.append(led.current_soll_array[point])
                tmp_density.append(led.current_density_array[point])
                tmp_wpe.append(led.wpe_array[point])
                tmp_eqe.append(led.eqe_array[point])
                tmp_op_power.append(led.op_power_array[point])
                tmp_j.append(led.j_array[point])
                count = count + 1

            # error
            self.voltage_array_std.append(np.std(tmp_voltage))
            self.current_array_std.append(np.std(tmp_current))
            self.current_density_array_std.append(np.std(tmp_density))
            self.wpe_array_std.append(np.std(tmp_wpe))
            self.eqe_array_std.append(np.std(tmp_eqe))
            self.op_power_array_std.append(np.std(tmp_op_power))
            self.j_array_std.append(np.std(tmp_j))

            # mean
            self.voltage_array_mean.append(np.mean(tmp_voltage))
            self.current_array_mean.append(np.mean(tmp_current))
            self.current_density_array_mean.append(np.mean(tmp_density))
            self.wpe_array_mean.append(np.mean(tmp_wpe))
            self.eqe_array_mean.append(np.mean(tmp_eqe))
            self.op_power_array_mean.append(np.mean(tmp_op_power))
            self.j_array_mean.append(np.mean(tmp_j))

            # clear tmp list
            tmp_voltage.clear()
            tmp_current.clear()
            tmp_density.clear()
            tmp_wpe.clear()
            tmp_eqe.clear()
            tmp_op_power.clear()
            tmp_j.clear()

        for leds in self.leds:
            tmp_iqe_max.append(leds.iqe_max)


        # data for table
        self.iqe_max_mean = np.mean(tmp_iqe_max)
        self.idx_wpe_max = np.array(self.wpe_array_mean).argmax(axis=0)
        self.wpe_mean_max = max(self.wpe_array_mean)
        self.wpe_abs_max = np.amax(np.asarray(self.wpe_array))
        self.j_at_wpe_max_mean = np.mean(np.array(self.j_at_wpe_max))
        self.j_at_wpe_max_std = np.std(np.array(self.j_at_wpe_max))

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
