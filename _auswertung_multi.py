import matplotlib.pyplot as plt
import auswertung_helper as static_m


class AuswertungExtensionMulti():

    color_wheel = ["black", "blue", "red", "green", "yellow", "cyan", "magenta", "black", "black", "black", "black"]
    marker_wheel = ["*", ",", "o", "v", ">", "s", "p", "1", "2", "3", "<", "^", "."]

    def __init__(self, filepath, limit_den_be, limit_den_end, limit_vol_beg, limit_vol_end, summary):
        self.filepath = filepath
        self.limit_x_axis_density_begin = limit_den_be
        self.limit_x_axis_density_end = limit_den_end
        self.limit_x_axis_voltage_begin = limit_vol_beg
        self.limit_x_axis_voltage_end = limit_vol_end
        self.summary_plot_paths = summary
        self.fontsize = 25

    def find_min_op(self, led_lists):
        op_idx_li = []
        for led_list in led_lists:
            op_idx = 0
            while led_list.current_density_array_mean[op_idx] == 0:
                op_idx = op_idx + 1
            op_idx_li.append(led_list.current_density_array_mean[op_idx + 1])

        return min(op_idx_li)

    async def plot_save_c_avg(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(24, 16))
        static_m.format_plot(plt, title, ax, self.fontsize)
        plt.xlim([self.find_min_op(led_lists), self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)
        color_cnt = 0
        static_m.scalar_formatter(ax)

        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            ax.plot(led_list.current_density_array_mean, led_list.op_power_array_mean, color="black", label = label, marker=self.marker_wheel[color_cnt], markersize="8")
            color_cnt = color_cnt + 1

        plt.legend(loc="upper left")
        file1 = file.replace(".csv", "_1.png")
        file_name1 = file1.split("/")[-1]
        path1 = f"{self.filepath}/{file_name1}_1"
        fig.savefig(path1)

        # format ax2
        fig, ax2 = plt.subplots(figsize=(24, 16))
        static_m.format_plot(plt, title, ax2, self.fontsize)
        plt.xlim([self.find_min_op(led_lists), self.limit_x_axis_density_end])
        ax2.set_xscale('log')
        ax2.grid(b=True, which='major', linestyle='-')
        ax2.grid(b=True, which='minor', linestyle='--')
        ax2.grid(True)

        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
        static_m.scalar_formatter(ax2)

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            ax2.plot(led_list.current_density_array_mean, led_list.wpe_array_mean, color="black", label=label, marker=self.marker_wheel[color_cnt], markersize="8")
            color_cnt = color_cnt + 1

        ax2.set_ylim(bottom=0)
        plt.legend(loc="upper left")

        file2 = file.replace(".csv", "_2.png")
        file_name2 = file2.split("/")[-1]
        path2 = f"{self.filepath}/{file_name2}_2"
        fig.savefig(path2)
        #self.summary_plot_paths.append(f"{path}.png")

    async def plot_allsizes_wpemax(self, file, title, led_lists):
        fig, ax = plt.subplots(figsize=(18, 12))
        static_m.format_plot(plt, title, ax, self.fontsize)
       # plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
       # ax.set_yscale('log')
        ax.set_xlabel("size in [µm]")
        ax.set_ylabel("wpe max")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)
        static_m.scalar_formatter(ax)

        color_cnt = 0
        for led_list in led_lists:
            first_led = led_list.leds[0]
            label = f"{round(first_led.LED_Dim_x * 10 ** 4)}µm"
            dim = [first_led.LED_Dim_x * 10 ** 4]
            max_wpe = [max(led_list.wpe_array_mean)]
            #ax.plot(x='x', y='y', ax=ax, kind='scatter', label=label)
            ax.plot(dim, max_wpe, "black", label = label, markersize=10, marker="o")
            color_cnt = color_cnt + 1

        ax.set_ylim(bottom=2.4)
        ax.set_xlim(left=0.9)


        #plt.legend(loc="upper left")


        file = file.replace(".csv", ".png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/{file_name}"
        fig.savefig(path)
        #self.summary_plot_paths.append(f"{path}.png")