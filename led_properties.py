import math
import numpy as np


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class LED:

    # led properties
    led_no = 0
    led_area = 0
    led_id = 0
    LED_Dim_x = 0.0
    LED_Dim_y = 0.0
    is_init = False
    is_shorted = False
    is_open_circuit = False
    is_malfunctioning = False

    # limits / constants
    lumefficency_blue = 42
    current_value = 20 * 10 ** (-6)
    OpPowerLimit = 10 ** -7
    OpenCircuitLimit = 10 ** -6
    voltage_start_wpe = 2
    IVL_NA = 0.91
    IVL_WPE_Collection = IVL_NA ** 2

    # measured data
    voltage_mess_array = []
    voltage_korr_array = []
    current_soll_array = []
    current_density_array = []
    op_power_array = []

    # calced data arrays
    wpe_array = []
    j_array = []
    wpe_ivl_array = []

    # calced data single
    op_power_current = 0
    op_power_max = 0
    voltage_start_wpe_index = 0
    CurrentValue_Index = 0
    op_power_3_3v = 0
    i_3_3v = 0
    wpe_current = 0

    # max
    wpe_max = 0
    wpe_ivl_max = 0
    wpe_max_index = 0
    j_at_wpe_max = 0
    j_max = 0
    i_max = 0

    # nits
    nits_max = 0
    nits_current_FF = 0
    nits_max_FF = 0
    nits_current = 0

    def __init__(self, led_no, led_area, led_id):
        self.led_no = led_no
        self.led_id = led_id
        self.led_area = led_area * 10 ** (-8)  # cm²
        self.LED_Dim_x = math.sqrt(self.led_area)
        self.LED_Dim_y = math.sqrt(self.led_area)

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
        self.wpe_array = 100 * self.op_power_array / (self.voltage_korr_array * self.current_soll_array)
        self.j_array = self.current_soll_array / ([self.led_area] * len(self.current_soll_array))
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

        # data for table
        voltage_3_3 = find_nearest(self.voltage_korr_array, value=3.3)
        self.i_3_3v = self.current_soll_array[voltage_3_3]
        self.op_power_3_3v = self.op_power_array[voltage_3_3]