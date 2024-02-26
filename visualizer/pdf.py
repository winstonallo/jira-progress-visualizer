from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

class PDF:

    def __init__(self, path : str, config : dict[str, str]):
        self.path = path

    def generate_pdf(self, issues):
        doc = SimpleDocTemplate(self.path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        for issue in issues:
            elements.append(Paragraph(issue, styles['Normal']))
        doc.build(elements)