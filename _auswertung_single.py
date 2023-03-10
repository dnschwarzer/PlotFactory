import numpy as np
import matplotlib.pyplot as plt


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


class AuswertungExtensionSingle():

    def __init__(self, led_list, filepath, limit_den_be, limit_den_end, limit_vol_beg, limit_vol_end, summary):
        self.led_list = led_list
        self.filepath = filepath
        self.limit_x_axis_density_begin = limit_den_be
        self.limit_x_axis_density_end = limit_den_end
        self.limit_x_axis_voltage_begin = limit_vol_beg
        self.limit_x_axis_voltage_end = limit_vol_end
        self.summary_plot_paths = summary
        self.fontsize = 25


    async def plot_save_c_sum(self, file, title, led_list):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title, fontsize=self.fontsize)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]")
        ax.set_ylabel("Opt. Power [W]")
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')

        for led in led_list.leds:
            if led.is_malfunctioning:
                continue
            ax.plot(led.current_density_array, led.op_power_array, "k")

        ax2 = ax.twinx()

        for led in led_list.leds:
            if led.is_malfunctioning:
                continue
            ax2.plot(led.current_density_array, led.wpe_array, 'b')

        ax2.set_xscale('log')
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        ax2.grid(False)

        file = file.replace(".csv", "_c_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/Output/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_c_fit(self, file, title):
        fig, ax = plt.subplots(figsize=(18, 12))

        # format ax 1
        ax.set_title(title, fontsize=self.fontsize)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        op_power = np.array(self.led_list.op_power_array_mean)
        current_density = np.array(self.led_list.current_density_array_mean)
        wpe_array = np.array(self.led_list.wpe_array_mean)

        # limit for ax
        idx_density_start = find_nearest(current_density, self.limit_x_axis_density_begin)

        x = current_density[idx_density_start:]
        y = op_power[idx_density_start:]
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 3)
        y_fit = np.exp(np.polyval(p, logx))
        ax.plot(x, y_fit, c='blue')
        ax.scatter(x, y, marker='o', c='black')

        # limits for fitting ax2
        idx_wpe_max = wpe_array.argmax(axis=0)
        j_at_wpe_max = self.led_list.current_array_mean[idx_wpe_max] / self.led_list.leds[0].led_area
        n = 3
        start_idx = find_nearest(self.led_list.j_array_mean, j_at_wpe_max / n)
        end_idx = find_nearest(self.led_list.j_array_mean, j_at_wpe_max * n)
        print(
            f"start index = {start_idx} J = {self.led_list.current_array_mean[start_idx] / self.led_list.leds[0].led_area} A/cm^2")
        print(
            f"end index = {end_idx} J = {self.led_list.current_array_mean[end_idx] / self.led_list.leds[0].led_area} A/cm^2")

        # ax 2
        ax2 = ax.twinx()

        x = current_density[start_idx:end_idx]
        y = wpe_array[start_idx:end_idx]
        # scale is log, therefore log values
        logx, logy = np.log(x), np.log(y)
        p = np.polyfit(logx, logy, 8)
        y_fit = np.exp(np.polyval(p, logx))
        ax2.plot(x, y_fit, c='blue')
        ax2.scatter(current_density[:start_idx], wpe_array[:start_idx], marker='o', c='blue')
        ax2.scatter(current_density[end_idx:], wpe_array[end_idx:], marker='o', c='blue')

        # format ax2
        ax2.grid(False)
        ax2.set_xscale('log')
        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        file = file.replace(".csv", "c_fit.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/Output/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    async def plot_save_c_avg(self, file, title, led_list):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title, fontsize=self.fontsize)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize - 1)
        ax.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax.grid(b=True, which='major', linestyle='-')
        ax.grid(b=True, which='minor', linestyle='--')
        ax.grid(True)

        ax.errorbar(led_list.current_density_array_mean,
                    led_list.op_power_array_mean, led_list.op_power_array_std,
                    fmt=',', linewidth=0.5, color='black',
                    markersize=0.1, capthick=1, capsize=5,
                    markeredgewidth=1)

        ax.scatter(led_list.current_density_array_mean, led_list.op_power_array_mean, s=4, linewidths=0.1,
                   color='black')

        file1 = file.replace(".csv", "c_avg_opt.png")
        file_name1 = file1.split("/")[-1]
        path1 = f"{self.filepath}/Output/{file_name1}_1"
        fig.savefig(path1)
        self.summary_plot_paths.append(f"{path1}.png")



        # format ax2
        fig, ax2 = plt.subplots(figsize=(18, 12))
        ax2.set_title(title, fontsize=self.fontsize)
        plt.xlim([self.limit_x_axis_density_begin, self.limit_x_axis_density_end])
        ax2.set_xscale('log')

        ax2.set_xlabel("Current density [A/cm²]", fontsize=self.fontsize - 1)
        ax2.set_ylabel("WPE [%]", fontsize=self.fontsize)
        ax2.grid(b=True, which='major', linestyle='-')
        ax2.grid(b=True, which='minor', linestyle='--')
        ax2.grid(True)
        from matplotlib.ticker import ScalarFormatter
        for axis in [ax2.xaxis, ax2.yaxis]:
            axis.set_major_formatter(ScalarFormatter())

        ax2.errorbar(led_list.current_density_array_mean, led_list.wpe_array_mean,
                     led_list.wpe_array_std,
                     fmt=',', linewidth=0.5, color='black',
                     markersize=0.1, capthick=1, capsize=5,
                     markeredgewidth=1)

        ax2.scatter(led_list.current_density_array_mean, led_list.wpe_array_mean, s=4, linewidths=0.1,
                    color='black')

        file2 = file.replace(".csv", "c_avg_opt2.png")
        file_name2 = file2.split("/")[-1]
        path2 = f"{self.filepath}/Output/{file_name2}_2"
        fig.savefig(path2)
        self.summary_plot_paths.append(f"{path2}.png")

    async def plot_save_avg_v(self, file, title, led_list):
        fig, host = plt.subplots(figsize=(18, 12))
        fig.subplots_adjust(left=0.20)
        host.set_title(title, fontsize=self.fontsize)

        host_col = "black"
        par1_col = "blue"
        par2_col = "black"

        par1 = host.twinx()
        par2 = host.twinx()
        host.grid(True)
        host.grid(b=True, which='major', linestyle='-')
        host.grid(b=True, which='minor', linestyle='--')
        plt.xlim([self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end])
        par2.spines["left"].set_position(("axes", -0.1))  # green one
        self.make_patch_spines_invisible(par2)
        par2.spines["left"].set_visible(True)
        par2.yaxis.set_label_position('left')
        par2.yaxis.set_ticks_position('left')

        idx = find_nearest(led_list.current_array_mean, 10 ** -6)
        idx = 0

        p1 = host.errorbar(led_list.voltage_array_mean[idx:],
                           led_list.current_array_mean[idx:], led_list.current_array_std[idx:],
                           fmt=',', linewidth=0.5, color=host_col,
                           markersize=0.1, capthick=1, capsize=5,
                           markeredgewidth=1)

        host.scatter(led_list.voltage_array_mean[idx:], led_list.current_array_mean[idx:], s=4, linewidths=0.1,
                   color=host_col)

        p2 = par1.errorbar(led_list.voltage_array_mean[idx:],
                           led_list.op_power_array_mean[idx:], led_list.op_power_array_std[idx:],
                           led_list.voltage_array_std[idx:],
                           fmt=',', linewidth=0.5, color=par1_col,
                           markersize=0.1, capthick=1, capsize=5,
                           markeredgewidth=1)

        par1.scatter(led_list.voltage_array_mean[idx:], led_list.op_power_array_mean[idx:], s=4, linewidths=0.1,
                   color=par1_col)

        p3 = par2.errorbar(led_list.voltage_array_mean[idx:],
                           led_list.current_density_array_mean[idx:],
                           led_list.current_density_array_std[idx:],
                           led_list.voltage_array_std[idx:],
                           fmt=',', linewidth=0.5, color=par2_col,
                           markersize=0.1, capthick=1, capsize=5,
                           markeredgewidth=1)

        par2.scatter(led_list.voltage_array_mean[idx:], led_list.current_density_array_mean[idx:], s=4,
                     linewidths=0.1,
                     color=par2_col)

        host.set_xlabel("Voltage [V]", fontsize=self.fontsize)
        host.set_ylabel("Current [A]", fontsize=self.fontsize)
        par2.set_ylabel("Current Density [A/cm²]", fontsize=self.fontsize)
        par1.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)

        host.set_yscale('log')
        par1.set_yscale('log')
        par2.set_yscale('log')

        host.yaxis.label.set_color(host_col)
        par1.yaxis.label.set_color(par1_col)
        par2.yaxis.label.set_color(par2_col)

        tkw = dict(size=4, width=1.5)
        host.tick_params(axis='y', colors=host_col, **tkw)
        par1.tick_params(axis='y', colors=par1_col, **tkw)
        par2.tick_params(axis='y', colors=par2_col, **tkw)
        host.tick_params(axis='x', **tkw)

        ###############################

        file = file.replace(".csv", "_avg.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/Output/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")

    def make_patch_spines_invisible(self, ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)

    async def plot_save_sum_v(self, file, title, led_list):
        fig, ax = plt.subplots(figsize=(18, 12))
        ax.set_title(title, fontsize=self.fontsize)
        # plt.ylim([10**-7, 10**-4])

        for led in led_list.leds:
            if not led.is_malfunctioning:
                ax.plot(led.voltage_korr_array, led.current_soll_array, "k")

        ax.set_xlabel("Voltage [V]", fontsize=self.fontsize)
        ax.set_ylabel("Current [A]", fontsize=self.fontsize)

        plt.xlim([self.limit_x_axis_voltage_begin, self.limit_x_axis_voltage_end])

        ax.grid(True)
        ax2 = ax.twinx()
        for led in led_list.leds:
            if not led.is_malfunctioning:
                ax2.plot(led.voltage_korr_array, led.op_power_array, 'b')

        ax2.grid(False)
        ax2.set_xlabel("Voltage [V]", fontsize=self.fontsize)
        ax2.set_ylabel("Opt. Power [W]", fontsize=self.fontsize)
        ax2.yaxis.label.set_color('blue')
        ax2.tick_params(axis='y', colors='blue')

        ax.set_yscale('log')
        ax2.set_yscale('log')

        file = file.replace(".csv", "_sum.png")
        file_name = file.split("/")[-1]
        path = f"{self.filepath}/Output/{file_name}"
        fig.savefig(path)
        self.summary_plot_paths.append(f"{path}.png")