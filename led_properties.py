import math
import numpy as np
import scipy.optimize as opt
import scipy

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class LED:

    def __init__(self, led_no, led_area, led_id):
        self.led_no = led_no
        self.led_id = led_id
        self.led_area = led_area * 10 ** (-8)  # cm²
        self.LED_Dim_x = math.sqrt(self.led_area)
        self.LED_Dim_y = math.sqrt(self.led_area)

        # led properties
        self.is_init = False
        self.is_shorted = False
        self.is_open_circuit = False
        self.is_malfunctioning = False

        # limits / constants
        self.lumefficency_blue = 42
        self.current_value = 20 * 10 ** (-6)
        self.OpPowerLimit = 10 ** -7
        self.OpenCircuitLimit = 10 ** -6
        self.voltage_start_wpe = 2
        self.IVL_NA = 0.91
        self.IVL_WPE_Collection = self.IVL_NA ** 2

        # measured data
        self.voltage_mess_array = []
        self.voltage_korr_array = []
        self.current_soll_array = []
        self.current_density_array = []
        self.op_power_array = []

        # calced data arrays
        self.wpe_array = []
        self.eqe_array = []
        self.eqe_fitted_array = []
        self.j_array = []
        self.wpe_ivl_array = []
        self.p_array = []


        # calced data single
        self.op_power_current = 0
        self.op_power_at_30mA = 0
        self.op_power_max = 0
        self.voltage_start_wpe_index = 0
        self.CurrentValue_Index = 0
        self.op_power_3_3v = 0
        self.i_3_3v = 0
        self.i_at_eqe_max = 0
        self.wpe_current = 0
        self.iqe = 0
        self.iqe_max = 0
        self.q = 0

        # max
        self.wpe_max = 0
        self.eqe_max = 0
        self.wpe_ivl_max = 0
        self.wpe_max_index = 0
        self.j_at_wpe_max = 0
        self.j_max = 0
        self.i_max = 0

        # nits
        self.nits_max = 0
        self.nits_current_FF = 0
        self.nits_max_FF = 0
        self.nits_current = 0

    def add_data(self, vol_mess, vol_korr, current_soll, current_dens, op_power):
        self.voltage_mess_array = np.asarray(vol_mess)
        self.voltage_korr_array = np.asarray(vol_korr)
        self.current_soll_array = np.asarray(current_soll)
        self.current_density_array = np.asarray(current_dens)
        self.op_power_array = np.asarray(op_power)

        # calc properties when all data was gathered
        self.calc()

    def calc(self):
        # WPE = P_opt / P_el
        self.wpe_array = np.asarray(100 * self.op_power_array) / np.asarray((self.voltage_korr_array * self.current_soll_array))
        self.j_array = np.asarray(self.current_soll_array) / np.asarray(([self.led_area] * len(self.current_soll_array)))
        last_op_value = self.op_power_array[len(self.op_power_array) - 1]
        last_current_value = self.current_soll_array[len(self.current_soll_array) - 1]

        if last_op_value > self.OpPowerLimit:
            self.is_open_circuit = False
            self.is_shorted = False
            self.is_malfunctioning = False
        elif last_current_value < self.OpenCircuitLimit:
            self.is_open_circuit = True
            self.is_malfunctioning = True
        else:
            self.is_shorted = True
            self.is_malfunctioning = True

        self.voltage_start_wpe_index = find_nearest(self.voltage_korr_array, value=self.voltage_start_wpe)
        idx_30mA = find_nearest(self.current_soll_array,  3.0 * 10 ** -5) # 30 mikro ampere
        self.op_power_at_30mA = self.op_power_array[idx_30mA]
        self.wpe_max = max(self.wpe_array)
        self.wpe_max_index = find_nearest(self.wpe_array, value=self.wpe_max)
        self.j_at_wpe_max = self.j_array[self.wpe_max_index]
        self.CurrentValue_Index = find_nearest(self.current_soll_array, value=self.current_value)

        if self.is_malfunctioning:
            wpe_at_current_index = 0
            self.wpe_max = 0
        else:
            wpe_at_current_index = self.wpe_array[self.CurrentValue_Index]
            self.op_power_current = self.op_power_array[self.CurrentValue_Index]
            # warum * 10 ^-12
            area = self.LED_Dim_x * self.LED_Dim_y * 10 ** -12
            ff = self.LED_Dim_x * self.LED_Dim_y / (18.5 * 18.5)
            self.nits_current = self.op_power_current * self.lumefficency_blue / (area * np.pi)
            self.nits_current_FF = self.nits_current * ff
            self.op_power_max = self.op_power_array[self.wpe_max_index]
            self.nits_max = self.op_power_max * self.lumefficency_blue / (area * np.pi)
            self.nits_max_FF = self.nits_max * ff
        self.wpe_current = wpe_at_current_index / self.IVL_WPE_Collection
        self.wpe_ivl_array = abs(self.wpe_array / self.IVL_WPE_Collection)
        self.wpe_ivl_max = self.wpe_max / self.IVL_WPE_Collection
        self.i_max = self.current_soll_array[self.wpe_max_index]
        self.j_max = max(self.j_array)

        # eqe, p etc
        self.eqe_array = self.wpe_array

        # fitting eqe and get eqe max over current, iqe
        self.eqe_fit_eqe_max()
        self.get_i_at_eqe_max()
        self.p_array = self.current_soll_array / self.i_at_eqe_max
        self.get_iqe_fit()

        # data for table
        voltage_3_3 = find_nearest(self.voltage_korr_array, value=3.3)
        self.i_3_3v = self.current_soll_array[voltage_3_3]
        self.op_power_3_3v = self.op_power_array[voltage_3_3]

    def eqe_fit_eqe_max(self):
        array_x, array_y = self.current_soll_array, self.eqe_array

        idx_wpe_max = array_y.argmax(axis=0)
        j_at_wpe_max = self.current_soll_array[idx_wpe_max] / self.led_area
        n = 3
        start_idx = find_nearest(self.j_array, j_at_wpe_max / n)
        end_idx = find_nearest(self.j_array, j_at_wpe_max * n)
        x = array_x[start_idx:end_idx]
        y = array_y[start_idx:end_idx]
        # scale is log, therefore log values
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 8)
        x3 = np.linspace(x[0], x[-1], 80)
        logx3 = np.log(x3)
        y_fit = np.exp(np.polyval(p, logx3))

        self.eqe_max = max(y_fit)

    def get_i_at_eqe_max(self):
        idx_eqe_max = find_nearest(self.eqe_array, self.eqe_max)
        self.i_at_eqe_max = self.current_soll_array[idx_eqe_max]

    def get_iqe_fit(self):
        array_x, array_y = self.p_array, self.eqe_array

        # only values after wpe max
        idx_eqe = find_nearest(self.eqe_array, self.eqe_max)
        array_x2 = self.p_array[:idx_eqe]
        array_y2 = self.eqe_array[:idx_eqe]

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
            sqrt_p_inv_array.append(1.0 / math.sqrt(val))

        array_x = np.add(sqrt_p_array, sqrt_p_inv_array)
        array_x2 = np.add(sqrt_p_array2, sqrt_p_inv_array2)
        array_y = self.eqe_max / array_y

        if len(array_x) > 0:
            end_idx = find_nearest(array_x, 4)
            x = array_x[:end_idx]
            y = array_y[:end_idx]

            if not len(x) <= 0 and np.isfinite(x).all() and np.isfinite(y).all():
                q_func = lambda x_param, q: (q + x_param) / (q + 2)
                popt, pcov = scipy.optimize.curve_fit(q_func, x, y)
                # more x vals
                xfine = np.linspace(array_x[0], array_x[-1], 100)
                p_fitted = q_func(xfine, popt[0])
                self.q = popt[0]
                self.iqe_max = self.q / (self.q + 2)
