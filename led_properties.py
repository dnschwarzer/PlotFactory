import math


class LED:

    led_no = 0
    led_area = 0
    led_id = 0
    LED_Dim_x = 0.0
    LED_Dim_y = 0.0
    is_init = False
    is_shorted = False
    is_open_circuit = False

    def __init__(self, led_no, led_area, led_id):
        self.led_no = led_no
        self.led_id = led_id
        self.led_area = led_area
        self.LED_Dim_x = math.sqrt(self.led_area)
        self.LED_Dim_y = math.sqrt(self.led_area)





