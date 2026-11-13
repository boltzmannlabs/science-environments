"""PDF layout helper for the offline benchmark report builder."""
from html import escape
from io import BytesIO
from pathlib import Path


class PDFReport:
    def __init__(self, title):
        import os
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        fonts = Path(os.environ.get('ENZYME_REPORT_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
        if not (fonts / 'DejaVuSans.ttf').is_file() or not (fonts / 'DejaVuSans-Bold.ttf').is_file():
            raise RuntimeError('Install DejaVu Sans fonts or set ENZYME_REPORT_FONT_DIR to their directory.')
        if 'ReportSans' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('ReportSans', str(fonts / 'DejaVuSans.ttf')))
            pdfmetrics.registerFont(TTFont('ReportSans-Bold', str(fonts / 'DejaVuSans-Bold.ttf')))
            pdfmetrics.registerFontFamily('ReportSans', normal='ReportSans', bold='ReportSans-Bold')
        self.title = title
        self.parts = []
        self.tables = []
        self.width = 770
        self.styles = {
            'body': ParagraphStyle('body', fontName='ReportSans', fontSize=9, leading=13,
                                   textColor=colors.HexColor('#243342'), spaceAfter=7),
            'cell': ParagraphStyle('cell', fontName='ReportSans', fontSize=7.5, leading=11),
            'caption': ParagraphStyle('caption', fontName='ReportSans', fontSize=8, leading=11,
                                      textColor=colors.HexColor('#4d5c69'), spaceAfter=8),
        }
        for level, size in [(0, 19), (1, 13), (2, 11)]:
            self.styles[level] = ParagraphStyle(str(level), parent=self.styles['body'],
                fontName='ReportSans-Bold', fontSize=size, leading=size + 5,
                textColor=colors.HexColor('#246b98'), spaceBefore=10 if level else 0,
                spaceAfter=8, keepWithNext=True)

    def add_heading(self, text, level):
        from reportlab.platypus import Paragraph
        self.parts.append(Paragraph(escape(text), self.styles[level]))

    def add_paragraph(self, text, style=None):
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph
        paragraph_style = self.styles['body']
        if style == 'keep_with_next':
            paragraph_style = ParagraphStyle('linked_body', parent=paragraph_style, keepWithNext=True)
        self.parts.append(Paragraph(escape(text), paragraph_style))

    def table(self, headers, values):
        from reportlab.lib import colors
        from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, KeepTogether
        def cell(value):
            return Paragraph(escape(str(value)), self.styles['cell'])
        fractions = {7: [.24, .10, .25, .11, .10, .10, .10],
                     5: [.23, .14, .13, .25, .25]}.get(len(headers), [1 / len(headers)] * len(headers))
        content = [[cell(h) for h in headers]] + [[cell(v) for v in row] for row in values]
        result = Table(content, colWidths=[self.width * x for x in fractions],
                       repeatRows=1, hAlign='LEFT')
        result.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f1f7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
            ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c7d4de')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        if result.wrap(self.width, 10000)[1] <= 300:
            self.parts.append(KeepTogether([result, Spacer(1, 8)]))
        else:
            self.parts.extend([result, Spacer(1, 8)])
        self.tables.append(result)

    def source(self, title, url):
        from reportlab.platypus import Paragraph
        self.parts.append(Paragraph(f'Source: <a color="#246b98" href="{escape(url, quote=True)}">'
                                    f'{escape(title)}</a>', self.styles['caption']))

    def add_figure(self, path, title, caption):
        from reportlab.platypus import Image, KeepTogether, Paragraph, Spacer
        picture = Image(BytesIO(Path(path).read_bytes()))
        scale = min(self.width / picture.imageWidth, 300 / picture.imageHeight)
        picture.drawWidth = picture.imageWidth * scale
        picture.drawHeight = picture.imageHeight * scale
        picture.hAlign = 'CENTER'
        self.parts.append(KeepTogether([
            Paragraph(escape(title), self.styles[2]), picture, Spacer(1, 5),
            Paragraph(escape(caption), self.styles['caption']),
        ]))

    def save(self, target):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate
        def footer(canvas, document):
            canvas.saveState()
            canvas.setFont('ReportSans', 7)
            canvas.setFillColor(colors.HexColor('#4d5c69'))
            canvas.drawString(36, 16, 'Enzyme variant optimization | Computational predictions')
            canvas.drawRightString(806, 16, f'Page {document.page}')
            canvas.restoreState()
        doc = SimpleDocTemplate(str(target), pagesize=landscape(A4),
            leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=32,
            title=self.title, author='Science environments',
            subject='Computational prediction comparison', creator='Offline benchmark report builder')
        self.width = doc.width
        doc.build(self.parts, onFirstPage=footer, onLaterPages=footer)
