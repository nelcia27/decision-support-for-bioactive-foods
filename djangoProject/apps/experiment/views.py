from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
import io, base64
from django.http.response import HttpResponse, FileResponse
import xlsxwriter
import json
from .forms import UploadFileForm
from .functions import handle_experiment_data, handle_radar_plot, handle_data_table, handle_bar_plot, handle_linear_plot

from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas

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
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    p.drawString(100, 100, "Hello world.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')


@csrf_exempt
def generatePlots(request):
    #{
    #   experiment_id:__,
    #   samples:[_], TYPE  ARRAY OF TYPE LIKE Sample.id
    #   plot_types:[__,__] TYPE ARRAY OF STRING,
    #   metrics:[] TYPE ARRAY OF TYPE LIKE Metrics.name
    #}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    arr = []
    table = handle_data_table(body['experiment_id'],body['samples'])
    
    for plot in body["plot_types"]:
        figs = []
        if plot.lower() == "radar":
            figs = handle_radar_plot(body['experiment_id'],body['samples'],table)
        elif plot.lower() == "bar":
            figs = handle_bar_plot(body['experiment_id'],body['samples'],table)
        elif plot.lower() == "linear":
            figs = handle_linear_plot(body['experiment_id'],body['samples'])
        for f in figs:
            buffer = io.BytesIO()
            f.savefig(buffer, format='png')
            to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
            arr.append(to_return)

    v = json.dumps(dict({
        "plots": arr,
        "raw_table": table
    }))

    response = HttpResponse(content_type="application/json")
    response.write(v)
    return response

