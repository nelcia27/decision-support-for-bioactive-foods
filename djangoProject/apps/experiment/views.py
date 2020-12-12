from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
import io
from django.http.response import HttpResponse
import xlsxwriter
import json


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


class ResultView(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    queryset = Result.objects.all()


class ExperimentView(viewsets.ModelViewSet):
    serializer_class = ExperimentSerializer
    queryset = Experiment.objects.all()

"""{
    "experiment_data" : ["test", "testowy", "www", "Kornelia", "06.12.2020"],
    "metrices" : [["1", "3", "3", "1", "1", ["120"], "wilgotność"]]
}"""


#request body:
#experiment_data, supplement_name, percentage_of_supplement, metrices
#experiment_data [nazwa,opis,link autor,data utworzenia]
#metrices list of lists of elements ['name','num_series', 'num_repeats', 'id_próbki', 'num_of_values_external_factor', 'list_of_values_external_factor', 'metrice_id']
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
        for i in [k for k in range(1, int(data[4]) + 1)]:
            series = "SERIA " + str(i)
            cell = 'B' + str(row_counter) + ":" + str(chr(ord('B') + int(data[4]) - 1)) + str(row_counter)
            if int(data[4]) - 1:
                worksheet.merge_range(cell, series, cell_format_blue)
            else:
                worksheet.write(cell, series, cell_format_blue)
            row_counter = row_counter + int(data[2])
            for j in range(1, int(data[2])):
                cellPomiar = 'A' + str(row_counter - j)
                to_write = "pomiar " + str(int(data[2]) - j)
                worksheet.write(cellPomiar, to_write, cell_format_blue)
                for b in range(0, len(data[5])):
                    cell = str(chr(ord('B') + b)) + str(row_counter - j)
                    worksheet.write(cell, "", unlocked)
    workbook.close()
    output.seek(0)

    filename = str(experiment_data[0]) + str(experiment_data[3]) + ".xlsx"
    #filename = "abc.xlsx"
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + filename
    output.close()

    return response


