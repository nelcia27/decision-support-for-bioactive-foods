from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from fpdf import FPDF
import io
from django.http.response import HttpResponse, FileResponse
import xlsxwriter
import json
from .forms import UploadFileForm
from .functions import handle_experiment_data
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from PIL import Image


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class BasicIngredientBaseView(viewsets.ModelViewSet):
    serializer_class = BasicIngredientBaseSerializer
    queryset = BasicIngredientBase.objects.all()


class BasicIngredientView(viewsets.ModelViewSet):
    serializer_class = BasicIngredientSerializer
    queryset = BasicIngredient.objects.all()


class RecipeView(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class SupplementBaseView(viewsets.ModelViewSet):
    serializer_class = SupplementBaseSerializer
    queryset = SupplementBase.objects.all()


class SupplementView(viewsets.ModelViewSet):
    serializer_class = SupplementSerializer
    queryset = Supplement.objects.all()


class ExternalFactorView(viewsets.ModelViewSet):
    serializer_class = ExternalFactorSerializer
    queryset = ExternalFactor.objects.all()


class SampleView(viewsets.ModelViewSet):
    serializer_class = SampleSerializer
    queryset = Sample.objects.all()


class MetricsView(viewsets.ModelViewSet):
    serializer_class = MetricsSerializer
    queryset = Metrics.objects.all()


class DetailedMetricsView(viewsets.ModelViewSet):
    serializer_class = DetailedMetricsSerializer
    queryset = DetailedMetrics.objects.all()


class ExperimentView(viewsets.ModelViewSet):
    serializer_class = ExperimentSerializer
    queryset = Experiment.objects.all()


class ResultView(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    queryset = Result.objects.all()

class PDF(FPDF):

    def header(self):
        title = 'System wspomagania decyzji do projektowania i oceny zywnosci bioaktywnej'
        # Arial bold 15
        self.set_font('Times', 'B', 16)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        # self.set_draw_color(0, 80, 180)
        self.set_draw_color(255, 255, 255)
        # self.set_fill_color(230, 230, 0)
        self.set_fill_color(255, 255, 255)
        # self.set_text_color(220, 50, 50)
        self.set_text_color(0, 0, 0)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Times', '', 14)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, num, name):
        self.set_font('Times', '', 12)
        if (num == 1):
            txt = name
            self.multi_cell(0, 5, txt, 0)
            self.ln()
        elif (num == 2 or num == 3):
            for txt in name:
                self.cell(0, 6, '- ' + txt, 0, ln=1)
            self.ln()
        elif (num == 4):
            for x in range(4):
                for y in range(5):
                    self.cell(30, 6, str(x) + 'x' + str(y), 1, ln=0)
                self.ln()
            self.ln()
            for x in range(6):
                for y in range(4):
                    self.cell(30, 6, str(x) + 'x' + str(y) + 'a', 1, ln=0)
                self.ln()
            self.ln()
            for x in range(4):
                for y in range(6):
                    self.cell(30, 6, str(x) + 'x' + str(y) + 'b', 1, ln=0)
                self.ln()
            self.ln()
        elif (num == 5):
            a = True
            #self.image('ikona.png')
        elif (num == 6):
            self.set_font('Times', 'U', 12)
            self.set_text_color(32, 32, 255)
            for txt in name:
                self.cell(0, 6, '- ' + txt, 0, ln=1)

    def lines(self):
        self.set_line_width(0.4)
        self.line(5.0, 5.0, 205.0, 5.0)  # top one
        self.line(5.0, 292.0, 205.0, 292.0)  # bottom one
        self.line(5.0, 5.0, 5.0, 292.0)  # left one
        self.line(205.0, 5.0, 205.0, 292.0)  # right one

    def print_chapter(self, num, title, name):
        # self.add_page()
        self.lines()
        self.chapter_title(num, title)
        self.chapter_body(num, name)


#metrices list of lists of elements ['name','num_series', 'num_repeats', 'id_próbki', 'num_of_values_external_factor', 'list_of_values_external_factor', 'metrice_id']
@csrf_exempt
def generate_experiment_excel(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    output = io.BytesIO()

    experiment_data = body['experiment_data']
    metrics = body['metrics']
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    locked = workbook.add_format()
    locked.set_locked(True)
    unlocked = workbook.add_format()
    unlocked.set_locked(False)
    unlocked.set_bg_color('#FFFFCC')
    unlocked.set_border()
    cell_format_blue = workbook.add_format()
    cell_format_blue.set_bg_color('#CCE5FF')
    cell_format_blue.set_border()

    worksheet = workbook.add_worksheet("opis_eksperymentu")
    worksheet.protect()
    worksheet.set_column('A:B', 60)
    worksheet.write('A1', str(experiment_data[0]), cell_format_blue)
    worksheet.write('A2', str(experiment_data[1]), cell_format_blue)
    worksheet.write('A3', str(experiment_data[2]), cell_format_blue)
    worksheet.write('A4', str(experiment_data[3]), cell_format_blue)
    worksheet.write('A5', str(experiment_data[4]), cell_format_blue)

    for data in metrics:
        worksheet_name = str(data[3]) + "," + str(data[0]) + "," + str(data[6])
        worksheet = workbook.add_worksheet(worksheet_name)
        worksheet.protect()
        how_wide = 1 + int(data[4])
        where_title = 'A1:' + str(chr(ord('A') + how_wide - 1)) + '1'
        worksheet.merge_range(where_title, data[0], cell_format_blue)
        counter = ord('B')
        for val in data[5]:
            cell = str(chr(counter)) + str(2)
            worksheet.write(cell, val, cell_format_blue)
            counter = counter + 1
            row_counter = 3
        for i in [k for k in range(1, int(data[1]) + 1)]:
            series = "SERIA " + str(i)
            cell = 'B' + str(row_counter) + ":" + str(chr(ord('B') + int(data[4]) - 1)) + str(row_counter)
            if int(data[1]) - 1:
                worksheet.merge_range(cell, series, cell_format_blue)
            else:
                worksheet.write(cell, series, cell_format_blue)
            row_counter = row_counter + int(data[2]) + 1
            for j in range(1, int(data[2])+1):
                cellPomiar = 'A' + str(row_counter - j)
                to_write = "pomiar " + str(int(data[2]) - j + 1)
                worksheet.write(cellPomiar, to_write, cell_format_blue)
                for b in range(0, len(data[5])):
                    cell = str(chr(ord('B') + b)) + str(row_counter - j)
                    worksheet.write(cell, "", unlocked)
    workbook.close()
    output.seek(0)

    filename = str(experiment_data[3]) + ".xlsx"
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + filename
    output.close()

    return response

@csrf_exempt
def read_experiment_data_from_xlsx(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_experiment_data(request.FILES['file'])
            return HttpResponse(status=200)
        print(form.errors)
    #else:
        #form = UploadFileForm()
    return HttpResponse(status=500)


@csrf_exempt
def generatePDF(request):
    title = 'System wspomagania decyzji do projektowania i oceny zywnosci bioaktywnej'
    ch1 = 'Opis'
    ch2 = 'Receptura'
    ch3 = 'Mierzone cechy'
    ch4 = 'Tabele'
    ch5 = 'Wizualizacja'
    ch6 = 'Linki'

    pdf = PDF()
    pdf.set_title(title)
    pdf.set_author('Zespol 4')
    pdf.add_page()
    pdf.print_chapter(1, ch1,
                      'Przygotowanie systemu do wspomagania analizy wynikow eksperymentów w zakresie receptur i technologii wytwarzania zywnosci bioaktywnej.')
    pdf.print_chapter(2, ch2, ['Maka Poznanska', 'Jajka', 'Woda', 'Sol'])
    pdf.print_chapter(3, ch3, ['Zujnosc', 'Twardosc', 'Wilgotnosc', 'Chrupkosc'])
    pdf.print_chapter(4, ch4, '')
    pdf.print_chapter(5, ch5, '')
    pdf.print_chapter(6, ch6, ['https://www.facebook.com/'])

    pdf.output('Eksperyment.pdf', 'F')
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    p.drawString(100, 100, "Hello world.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

@csrf_exempt
def generatePlots(request):
    red = Image.new('RGB', (1, 1), (255,0,0,0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response

@csrf_exempt
def generateStats(request):
    red = Image.new('RGB', (1, 1), (255,0,0,0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response