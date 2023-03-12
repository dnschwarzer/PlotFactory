from fpdf import FPDF
import pathlib
import os
import numpy as np
import LedList
import PySimpleGUI as sg

class PDF(FPDF):

    title = ""
    subtext = ""

    def __init__(self, title, subtext):
        self.title = title.replace("--", " ")
        self.subtext = subtext
        super(PDF, self).__init__()

    def header(self):
        # Logo
        logo_path = f"{pathlib.Path().resolve()}/res/Rastergrafik.ico"

        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.ln(4)
        self.cell(0, 10, self.title, 0, 1, align='C')
        self.ln()

        self.image(logo_path, 10, 8, 33)

       # self.cell(h=10, txt=self.title, border=1, align='C')
        # Line break
        self.ln(5)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Properties: ' + str(self.subtext) + '\n' + 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def create_pdf(self, image_path, file_path, file_name):
        pdf = PDF(self.title)
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('helvetica', size=12)
        pdf.ln(15)
        pdf.cell(txt=file_name)

        for paths in image_path:
            pdf.ln()
            pdf.image(w=pdf.epw, name=paths)
            pdf.add_page()
            pdf.ln()
            pdf.ln()
            pdf.ln()

        for path in image_path:
            if os.path.isfile(path):
                os.remove(path)

        pdf.set_font('helvetica', size=7)

        for i in range(0, 8):
            for j in range(0, 8):
                pdf.cell(20, 10, f"slave_no_{i}x{j}", 1, 0, 'C')
            pdf.ln()

        pdf.set_font('helvetica', size=12)

        pdf.ln(5)

        for i in range(1, 8):
            pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)

        pdf.output(file_path)

    def create_summary_pdf(self, image_path, file_path, file_name, led_list: LedList.LedList):
        pdf = self
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('helvetica', size=15)
        pdf.ln()
        pdf.cell(0, 10, file_name , 0, 1, align='C')

        # add all summary plots
        for paths in image_path:
            pdf.ln()
            pdf.image(w=pdf.epw, name=paths)
            pdf.add_page()
            pdf.ln()

        # overview table
        pdf.cell(0, 10, 'Overview', 0, 1, align='C')
        pdf.ln()

        cell_width = 21
        cell_width_id = 15
        cell_height = 7
        cell_margin = 7
        pdf.set_font('helvetica', size=7)
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')

        title_list = []
        title_list.append("LED ID")
        title_list.append("J max [A/cm²]")
        title_list.append("WPE max")
        title_list.append("J at WPE max [A/cm²]")
        title_list.append("I 3.3 V [A]")
        title_list.append("op. Power 3.3 V [W]")
        title_list.append("op. Power 30µA [W]")
        title_list.append("IQE max [%]")

        column_count = len(title_list)

        pdf.set_font('helvetica', size=5)

        for col in range(0, column_count):
            if title_list[col] == "LED ID":
                pdf.cell(cell_width_id, cell_height, title_list[col], 1, 0, 'C')
            else:
                pdf.cell(cell_width, cell_height, title_list[col], 1, 0, 'C')

        pdf.set_font('helvetica', size=7)

        pdf.ln()

        for led in led_list.leds:
            pdf.set_x(cell_margin)
            # first blank cell
            pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
            # second id cell
            pdf.cell(cell_width_id, cell_height, f"Q{led.led_no} ID{led.led_id}", 1, 0, 'C')
            if led.is_shorted and not led.is_open_circuit:
                for col in range(0, column_count - 1):
                    pdf.cell(cell_width, cell_height, f"SC", 1, 0, 'C')

            elif led.is_open_circuit and not led.is_shorted:
                for col in range(0, column_count - 1):
                    pdf.cell(cell_width, cell_height, f"OC", 1, 0, 'C')

            elif not led.is_open_circuit and not led.is_shorted and led.is_malfunctioning:
                for col in range(0, column_count - 1):
                    pdf.cell(cell_width, cell_height, f"ME", 1, 0, 'C')

            else:
                val_table = [
                    led.j_max,
                    led.wpe_max,
                    led.j_at_wpe_max,
                    led.i_3_3v,
                    led.op_power_3_3v,
                    led.op_power_at_30mA,
                    led.iqe_max * 10 ** 2,
                ]
                decimals = 3
                for val in val_table:
                    pdf.cell(cell_width, cell_height, f"{float(val):.{decimals}}", 1, 0, 'C')

            pdf.ln()

        # summary and average table of overview
        j_max = []
        wpe_max = []
        i_3_3v = []
        op_power_3_3v = []
        o_30mA = []
        iqe_max = []
        for led in led_list.leds:
            # ignore malfunctioning leds
            if led.is_malfunctioning:
                continue

            j_max.append(led.j_max)
            wpe_max.append(led.wpe_max)
            i_3_3v.append(led.i_3_3v)
            op_power_3_3v.append(led.op_power_3_3v)
            o_30mA.append(led.op_power_at_30mA)
            iqe_max.append(led.iqe_max)

        val_table = [
            j_max,
            wpe_max,
            led_list.j_at_wpe_max_mean,
            i_3_3v,
            op_power_3_3v,
            o_30mA,
            iqe_max * 10 ** 2,
        ]
        decimals = 3

        # avg
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"arithmetic mean", 1, 0, 'C')
        pdf.cell(cell_width_id, cell_height, f"", 1, 0, 'C')
        for val in val_table:
            pdf.cell(cell_width, cell_height, f"{float(np.mean(val)):.{decimals}}", 1, 0, 'C')
        pdf.ln()

        # std deviation
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"std deviation", 1, 0, 'C')
        pdf.cell(cell_width_id, cell_height, f"", 1, 0, 'C')
        for val in val_table:
            pdf.cell(cell_width, cell_height, f"{float(np.std(val)):.{decimals}}", 1, 0, 'C')
        pdf.ln()
        pdf.ln()

        # malfunctioning led summary table
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"SC Count", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{led_list.is_shorted_cnt}", 1, 0, 'C')
        pdf.ln()
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"OC Count", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{led_list.is_open_circuit_cnt}", 1, 0, 'C')
        pdf.ln()
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"sum", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{led_list.is_shorted_cnt + led_list.is_open_circuit_cnt}", 1, 0, 'C')
        ###################################################

        try:
            pdf.output(file_path)
        except PermissionError:
            sg.Popup("pdf already open, close pdf and click ok")
            pdf.output(file_path)


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


