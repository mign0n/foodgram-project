import csv
import io

from rest_framework import renderers

FILE_HEADERS = (
    'id',
    'name',
    'amount',
    'measurement_unit',
)


class CSVRecipeDataRenderer(renderers.BaseRenderer):
    media_type = "text/csv"
    format = "csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(
            csv_buffer, fieldnames=FILE_HEADERS, extrasaction="ignore"
        )
        csv_writer.writeheader()

        for item in data:
            csv_writer.writerow(item)

        return csv_buffer.getvalue()


class TextRecipeDataRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        text_buffer = io.StringIO()
        text_buffer.write(' '.join(header for header in FILE_HEADERS) + '\n')

        for item in data:
            text_buffer.write(
                ' '.join(str(values) for values in list(item.values())) + '\n'
            )

        return text_buffer.getvalue()
