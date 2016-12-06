# coding=utf-8
import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Flowable, Paragraph, Table, TableStyle, Spacer, Frame, KeepInFrame

from clock.pages.templatetags.format_duration import format_dttd

# Register custom fonts. Path is hardcoded so we're using the internal fonts from /static/
pdfmetrics.registerFont(TTFont('OpenSans-Regular', os.path.join(str(settings.APPS_DIR),
                                                                'static/common/fonts/opensans/OpenSans-Regular.ttf')))
pdfmetrics.registerFont(TTFont('OpenSans-Bold', os.path.join(str(settings.APPS_DIR),
                                                             'static/common/fonts/opensans/OpenSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('OpenSans-Italic', os.path.join(str(settings.APPS_DIR),
                                                               'static/common/fonts/opensans/OpenSans-Italic.ttf')))


class BoxyLine(Flowable):
    """
    Draw a box + line + text

    -----------------------------------------
    | foobar |
    ---------

    """

    # ----------------------------------------------------------------------
    def __init__(self, x=0, y=-15, width=40, height=15, text_label="", text_box=""):
        Flowable.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text_box = text_box
        self.text_label = text_label
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='HeadText', fontName='OpenSans-Regular', fontSize=10))

    # ----------------------------------------------------------------------
    def coord(self, x, y, unit=1):
        """
        http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
        Helper class to help position flowables in Canvas objects
        """
        x, y = x * unit, self.height - y * unit
        return x, y

    # ----------------------------------------------------------------------
    def draw(self):
        """
        Draw the shape, text, etc
        """
        self.canv.rect(self.x + 140, self.y + 2, self.width - 155, self.height)

        p = Paragraph(self.text_label, style=self.styles["HeadText"])
        p.wrapOn(self.canv, self.width, self.height)
        if self.text_label == "Monat / Jahr":
            p.drawOn(self.canv, *self.coord(self.x - 100, 3, mm))
        else:
            p.drawOn(self.canv, *self.coord(self.x + 2, 10, mm))

        p = Paragraph(self.text_box, style=self.styles["HeadText"])
        p.wrapOn(self.canv, self.width, self.height)
        if self.text_label == "Monat / Jahr":
            p.drawOn(self.canv, *self.coord(self.x - 74, 3, mm))
        else:
            p.drawOn(self.canv, *self.coord(self.x + 53, 10, mm))


class ShiftExport:
    def __init__(self, context, buffer, pagesize, *args, **kwargs):
        self.buffer = buffer
        self.context = context
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # canvas.setTitle("Shift export")
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='NormalText', fontName='OpenSans-Regular', fontSize=10))
        styles.add(ParagraphStyle(name='BottomText', fontName='OpenSans-Regular', fontSize=8))
        styles.add(ParagraphStyle(name='Schluessel', alignment=TA_CENTER, fontName='OpenSans-Regular', fontSize=14))
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER, fontName='OpenSans-Regular'))

        # Text that is found on the bottom of (right now..) every page!
        canvas.setFillColor(colors.lightgrey)
        canvas.rect(200, doc.bottomMargin, 125, 40, fill=True)
        frame1 = Frame(200, doc.bottomMargin, 125, 40, showBoundary=1, topPadding=10)

        story = [Paragraph('Schlüssel', styles['Schluessel'])]
        story_inframe = KeepInFrame(4 * inch, 8 * inch, story)
        frame1.addFromList([story_inframe], canvas)

        key_text = Paragraph("K Krank<br /><br />U Urlaub", styles['NormalText'])
        w, h = key_text.wrap(doc.width, doc.bottomMargin)
        key_text.drawOn(canvas, 200 + 125 + 5, doc.bottomMargin + 2.5 )

        note_text = Paragraph("* Tragen Sie in diese Spalte eines der folgenden Kürzel ein, wenn es für diesen "
                              "Kalendertag zutrifft", styles['BottomText'])
        w, h = note_text.wrap(doc.width, doc.bottomMargin)
        note_text.drawOn(canvas, doc.leftMargin + 5, doc.bottomMargin + 45)

        status_text = Paragraph("Stand: 10/2015", styles['BottomText'])
        w, h = status_text.wrap(doc.width, doc.bottomMargin)
        status_text.drawOn(canvas, doc.width - 5 * mm, doc.bottomMargin)

        # Release the canvas
        canvas.restoreState()

    @property
    def print_shifts(self):
        # Grab current month date-object and prepare the PDF title
        date = self.context['month']
        pdfTitle = 'Arbeitsstunden ' + date.strftime('%B %Y')

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                pagesize=self.pagesize,
                                title=pdfTitle)

        # Our container for 'Flowable' objects
        elements = []

        # Define styles we'll use in this main thing
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='NormalText', fontName='OpenSans-Regular', fontSize=10))
        styles.add(ParagraphStyle(name='NormalCenteredText', alignment=TA_CENTER, fontName='OpenSans-Regular', fontSize=10))
        styles.add(ParagraphStyle(name='BoldText', alignment=TA_CENTER, fontName='OpenSans-Bold', fontSize=10))
        styles.add(ParagraphStyle(name='TitleBoldCentered', alignment=TA_CENTER, fontName='OpenSans-Bold', fontSize=12))
        styles.add(ParagraphStyle(name='TitleCentered', alignment=TA_CENTER, fontName='OpenSans-Regular', fontSize=10))

        # Add text on top of the first page
        elements.append(Paragraph(u'Vorlage zur Dokumentation der täglichen Arbeitszeit nach § 17 MiLoG<br /><br />'
                                  u'Wichtig:', styles['TitleBoldCentered']))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(u'Die Aufzeichnungen sind mindestens wöchentlich zu führen, denn es besteht '
                                  u'die Verpflichtung </para><para fontName="OpenSans-Italic">"Beginn, Ende und Dauer '
                                  u'der täglichen Arbeitszeit spätestens bis zum Ablauf des siebten auf den Tag der '
                                  u'Arbeitsleistung folgenden Kalendertages aufzuzeichnen und diese Aufzeichnungen '
                                  u'mindestens zwei Jahre beginnend ab dem für die Aufzeichnung maßgelblichen '
                                  u'Zeitpunkt aufzubewahren.“',
                                  styles['TitleCentered']))
        elements.append(Spacer(1, 6))

        # Add boxes above the table
        boxes = [BoxyLine(width=doc.width, height=20, text_label="FB / Institut / Abteilung",
                          text_box=self.context['department']), Spacer(1, 4),
                 BoxyLine(width=doc.width, height=20, text_label="Name des Mitarbeiters",
                          text_box=self.context['fullname']), Spacer(1, 4),
                 BoxyLine(width=100 + 155, height=20, text_label="Pers. Nr. (falls vorhanden)",
                          text_box=""),
                 BoxyLine(x=196, y=+5, width=100 + 155, height=20, text_label="Monat / Jahr",
                          text_box=date.strftime("%m") + " / " + date.strftime("%Y"))]
        for box in boxes:
            elements.append(box)

        elements.append(Spacer(1, 18))

        # Prepare header line and append it to the table list
        h1_date = Paragraph('''Datum''', styles["BoldText"])
        h2_start = Paragraph('''Beginn<br />(Uhrzeit)''', styles["BoldText"])
        h3_pause = Paragraph('''Pause<br />(von - bis)''', styles["BoldText"])
        h4_end = Paragraph('''Ende<br />(Uhrzeit)''', styles["BoldText"])
        h5_total = Paragraph('''Dauer<br />(Summe ohne Pausen)''', styles["BoldText"])
        h6_cmnt = Paragraph('''*''', styles["BoldText"])
        table_data = [[h1_date, h2_start, h3_pause, h4_end, h5_total, h6_cmnt]]

        shifts = self.context['shift_list']

        # Go through all shifts and format them accordingly
        i = 0
        for i, shift in enumerate(shifts):
            # Not sure why, but timezone.localtime() is not working here.
            # Instead timezone.template_localtime() is, so we're using it.. dum-dee-doo..
            b1_date = timezone.template_localtime(shift.shift_started).strftime('%d.%m.%Y')  # e.g. 24.12.2016
            b2_start = timezone.template_localtime(shift.shift_started).strftime("%H:%M")  # e.g. 08:15
            b3_pause = shift.pause_start_end  # e.g. 08:15 - 15:55
            b4_end = timezone.template_localtime(shift.shift_finished).strftime("%H:%M")  # e.g. 15:55
            b5_total = format_dttd(shift.shift_duration, "%H:%M")  # e.g. 07:40
            b6_cmnt = shift.key  # e.g. "K" or "U"

            # We want every cell content to be an own paragraph, so we can give it a certain style.
            # As always there is probably some other smart solution, but this works.
            body_row = []
            body_cells = [b1_date, b2_start, b3_pause, b4_end, b5_total, b6_cmnt]
            for cell in body_cells:
                body_row.append(Paragraph(cell, styles['NormalCenteredText']))
            table_data.append(body_row)

        # Append new empty lines while we haven't reached the full page capacity!
        if i < 18:
            f = i
            while f < 19:
                table_data.append(['', '', '', '', '', ''])
                f += 1

        total_shift_duration = ''
        if self.context['total_shift_duration'] > timedelta(seconds=0):
            total_shift_duration = format_dttd(self.context['total_shift_duration'], "%H:%M")
        table_data.append(['', '', '', 'Summe:', total_shift_duration, ''])

        # Create the table. Column width are set to fit the current data correctly.
        shift_table = Table(table_data, colWidths=(22.5*mm, 22.5*mm, 27.5*mm, 22.5*mm, 45*mm, 12.5*mm))
        shift_table.setStyle(TableStyle([
                                        ('INNERGRID', (0, 0), (-1, -2), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -2), 0.25, colors.black),
                                        ('INNERGRID', (3, -1), (4, -1), 0.25, colors.black),  # Custom grid for last row
                                        ('BOX', (3, -1), (4, -1), 0.25, colors.black),  # Custom border for last row
                                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ]))
        elements.append(shift_table)
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,)
                  # canvasmaker=NumberedCanvas)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
