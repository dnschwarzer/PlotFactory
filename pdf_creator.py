import numpy
from fpdf import FPDF
import pathlib
import os
import numpy as np


class TableData:
    no = "led"
    id = "led"
    j_wpe_max = 0
    wpe_max = 0
    i_3_3v = 0
    op_power_3_3v = 0

    is_shorted = False
    is_open = False

    def __init__(self, no, identity, j_wpe_max, wpe_max, i_3_3v, op_power_3_3v, is_shorted, is_open):
        self.no = no
        self.id = identity
        self.j_wpe_max = j_wpe_max
        self.wpe_max = wpe_max
        self.i_3_3v = i_3_3v
        self.op_power_3_3v = op_power_3_3v
        self.is_shorted = is_shorted
        self.is_open = is_open

    def as_array(self):
        return [self.no, self.id, self.j_wpe_max, self.wpe_max, self.i_3_3v, self.op_power_3_3v]


class PDF(FPDF):

    title = ""

    def __init__(self, title):
        self.title = title.replace("--", " ")
        super(PDF, self).__init__()

    def header(self):
        # Logo
        logo_path = f"{pathlib.Path().resolve()}/res/Rastergrafik.ico"

        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.ln(4)
        self.cell(0, 10, self.title, 1, 1, align='C')
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
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

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

    def create_summary_pdf(self, image_path, file_path, file_name, led_data: TableData, malfunc_leds: TableData):
        pdf = self
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('helvetica', size=15)
        pdf.ln(5)
        pdf.cell(0, 10, 'Summary', 0, 1, align='C')

        # add all summary plots
        for paths in image_path:
            pdf.ln()
            pdf.image(w=pdf.epw, name=paths)
            pdf.add_page()
            pdf.ln()

        # overview table
        pdf.cell(0, 10, 'Overview', 0, 1, align='C')
        pdf.ln()

        cell_width = 25
        cell_height = 7
        cell_margin = 25
        pdf.set_font('helvetica', size=7)
        pdf.set_x(cell_margin)

        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"LED ID", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"J max", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"WPE max", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"I 3.3V", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"op. Power 3.3", 1, 0, 'C')
        pdf.ln()

        for i in range(0, len(led_data)):
            current_led = led_data[i].as_array()
            pdf.set_x(cell_margin)
            for j in range(0, len(current_led)):
                # first blank cell
                if j == 0:
                    pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
                # second id cell
                elif j == 1:
                    pdf.cell(cell_width, cell_height, f"Q{led_data[i].no} ID{led_data[i].id}", 1, 0, 'C')
                # others: values
                else:
                    if led_data[i].is_shorted:
                        pdf.cell(cell_width, cell_height, f"short circuit", 1, 0, 'C')
                    elif led_data[i].is_open:
                        pdf.cell(cell_width, cell_height, f"open circuit", 1, 0, 'C')
                    else:
                        value_to_print = current_led[j]
                        if isfloat(value_to_print):
                            f = value_to_print
                            n = 3
                            value_to_print = f'{float(f):.{n}}'
                        pdf.cell(cell_width, cell_height, f"{value_to_print}", 1, 0, 'C')
            pdf.ln()

        # summary and average table of overview
        j_max = []
        wpe_max = []
        i_3_3v = []
        op_power_3_3v = []
        for i in range(0, len(led_data)):
            # ignore malfunctioning leds
            if led_data[i].is_open or led_data[i].is_shorted:
                continue

            led_arr = led_data[i].as_array()
            j_max.append(led_arr[2])
            wpe_max.append(led_arr[3])
            i_3_3v.append(led_arr[4])
            op_power_3_3v.append(led_arr[5])

        # avg
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"arithmetic mean", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(j_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(wpe_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(i_3_3v):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.mean(op_power_3_3v):.{3}}", 1, 0, 'C')
        pdf.ln()

        # std deviation
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"std deviation", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(j_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(wpe_max):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(i_3_3v):.{3}}", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{np.std(op_power_3_3v):.{3}}", 1, 0, 'C')
        pdf.ln()
        pdf.ln()

        # malfunctioning led summary table
        sc_count = 0
        oc_count = 0

        for mal in malfunc_leds:
            if mal.is_shorted:
                sc_count = sc_count + 1
            if mal.is_open:
                oc_count = oc_count + 1

        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"SC Count", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{sc_count}", 1, 0, 'C')
        pdf.ln()
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"OC Count", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{oc_count}", 1, 0, 'C')
        pdf.ln()
        pdf.set_x(cell_margin)
        pdf.cell(cell_width, cell_height, f"sum", 1, 0, 'C')
        pdf.cell(cell_width, cell_height, f"{oc_count + sc_count}", 1, 0, 'C')
        ###################################################

        pdf.output(file_path)


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


