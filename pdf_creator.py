from fpdf import FPDF
import pathlib

class PDF(FPDF):
    def header(self):
        # Logo
        logo_path = f"{pathlib.Path().resolve()}/res/Rastergrafik.ico"

        self.image(logo_path, 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, "vlad slave", 1, 0, 'C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


def create_pdf(image_path, file_path, file_name):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('helvetica', size=12)
    pdf.ln(15)
    pdf.cell(txt=file_name)
    pdf.ln()
    pdf.image(w=pdf.epw, name=image_path)
    pdf.ln(1)

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