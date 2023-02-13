from fpdf import FPDF
import pathlib
import os
import numpy as np
import LedList

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

        cell_width = 30
        cell_height = 7
        cell_margin = 7
        pdf.set_font('helvetica', size=7)
        pdf.set_x(cell_margin)

        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"LED ID", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"J max [A/cm^2]", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"WPE max", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"J at WPE max [A/cm^2]", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"I 3.3 V [A]", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"op. Power 3.3 V [W]", 1, 0, 'C')
        pdf.ln()

        for led in led_list.leds:
            pdf.set_x(cell_margin)
            # first blank cell
            pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
            # second id cell
            pdf.cell(cell_width, cell_height, f"Q{led.led_no} ID{led.led_id}", 1, 0, 'C')
            if led.is_shorted and not led.is_open_circuit:
                pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')

            elif led.is_open_circuit and not led.is_shorted:
                pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')

            elif not led.is_open_circuit and not led.is_shorted and led.is_malfunctioning:
                pdf.cell(cell_width, cell_height, f"measure error", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"measure error", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"measure error", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"measure error", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"measure error", 1, 0, 'C')

            else:
                n = 3
                pdf.cell(cell_width, cell_height, f"{float(led.j_max):.{n}}", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"{float(led.wpe_max):.{n}}", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"{float(led.j_at_wpe_max):.{n}}", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"{float(led.i_3_3v):.{n}}", 1, 0, 'C')
                pdf.cell(cell_width, cell_height, f"{float(led.op_power_3_3v):.{n}}", 1, 0, 'C')
            pdf.ln()

        # summary and average table of overview
        j_max = []
        wpe_max = []
        i_3_3v = []
        op_power_3_3v = []
        for led in led_list.leds:
            # ignore malfunctioning leds
            if led.is_malfunctioning:
                continue

            j_max.append(led.j_max)
            wpe_max.append(led.wpe_max)
            i_3_3v.append(led.i_3_3v)
            op_power_3_3v.append(led.op_power_3_3v)

        # avg
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"arithmetic mean", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(j_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(wpe_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{led_list.j_at_wpe_max_mean:.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(i_3_3v):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(op_power_3_3v):.{3}}", 1, 0, 'C')
        pdf.ln()

        # std deviation
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"std deviation", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(j_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(wpe_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{led_list.j_at_wpe_max_std:.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(i_3_3v):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(op_power_3_3v):.{3}}", 1, 0, 'C')
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

        pdf.output(file_path)


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


