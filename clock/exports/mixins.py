from io import BytesIO

from django.http import HttpResponse

from clock.exports.printing import ShiftExport


class PdfResponseMixin(object):

    def render_to_response(self, context, **response_kwargs):
        filename = "Stundenzettel_{}_.pdf".format(context["month"].strftime("%Y%m"))

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=" + filename

        buffer = BytesIO()

        report = ShiftExport(context, buffer, "A4")
        pdf = report.print_shifts

        response.write(pdf)
        return response
