from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from fpdf import FPDF
import io, base64, os
import io, base64
from django.http.response import HttpResponse, FileResponse
import xlsxwriter
import json
from .forms import UploadFileForm
from .functions import handle_experiment_data, handle_radar_plot, handle_data_table, handle_bar_plot, \
    handle_linear_plot, truncate
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from PIL import Image
from .functions import stats_data
import requests as req
from django.contrib.auth import get_user_model

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


title = ''


class PDF(FPDF):

    def header(self):
        self.add_font('DejaVuB', '', 'DejaVuSansCondensed-BoldOblique.ttf', uni=True)
        self.set_font('DejaVuB', '', 16)
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
        self.set_font('DejaVu', '', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'DejaVu ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('DejaVu', '', 14)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, '%s' % (label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, num, name):
        self.set_font('DejaVu', '', 12)
        if (num == 1):
            txt = name
            self.multi_cell(0, 5, txt, 0)
            self.ln()
        elif (num == 2):
            self.set_font(family='DejaVuB', style='')
            self.multi_cell(0, 6, 'Podstawa:', 0)
            self.set_font(family='DejaVu', style='')
            for txt in name[0]:
                self.multi_cell(0, 6, '- ' + txt, 0)
            self.ln()
            self.set_font(family='DejaVuB', style='')
            self.multi_cell(0, 6, 'Dodatki:', 0)
            self.set_font(family='DejaVu', style='')
            for txt in name[1]:
                self.multi_cell(0, 6, '- ' + txt, 0)
            self.ln()
        elif (num == 3):
            for txt in name:
                self.multi_cell(0, 6, '- ' + txt, 0)
            self.ln()
        elif (num == 4):
            for tab in name:
                metric = tab[0]
                ex_factors = tab[1]
                data = tab[2]
                mean = tab[3]
                dev = tab[4]

                self.cell(30, 6, ' ', 0, ln=0)
                self.cell(30 * len(data[0][0]), 6, metric, 0, ln=0)
                self.ln()

                self.set_fill_color(r=125, g=205, b=125)

                self.cell(30, 6, ' ', 0, ln=0)
                for ex in ex_factors:
                    self.cell(30, 6, ex, 1, ln=0, fill=True)
                self.ln()

                series_num = 1
                truncate(12.3456, 2)
                for x in data:
                    self.set_fill_color(r=211, g=0, b=0)
                    self.cell(30, 6, ' ', 0, ln=0)
                    self.cell(30 * len(x[0]), 6, 'Seria ' + str(series_num), 1, ln=0, fill=True)
                    self.ln()
                    measuer_num = 1
                    for y in x:
                        self.set_fill_color(r=211, g=0, b=0)
                        self.cell(30, 6, 'Pomiar ' + str(measuer_num), 1, ln=0, fill=True)
                        for z in y:
                            self.set_fill_color(r=255, g=250, b=205)
                            self.cell(30, 6, str(truncate(z, 4)), 1, ln=0, fill=True)
                        self.ln()
                        measuer_num += 1

                    self.set_fill_color(r=192, g=192, b=192)
                    self.cell(30, 6, 'Srednia serii', 1, ln=0, fill=True)
                    self.set_fill_color(r=225, g=225, b=225)
                    for z in mean[series_num - 1]:
                        self.cell(30, 6, str(truncate(z, 4)), 1, ln=0, fill=True)
                    self.ln()

                    self.set_fill_color(r=192, g=192, b=192)
                    self.cell(30, 6, 'Odchylenie stand.', 1, ln=0, fill=True)
                    self.set_fill_color(r=225, g=225, b=225)
                    for z in dev[series_num - 1]:
                        self.cell(30, 6, str(truncate(z, 4)), 1, ln=0, fill=True)
                    self.ln()
                    series_num += 1

                self.ln()

        elif (num == 5):
            for img in name:
                self.image(img)
                os.remove(img)
        elif (num == 6):
            self.set_font('DejaVu', '', 12)
            self.set_text_color(32, 32, 255)
            for txt in name:
                self.cell(0, 6, '- ' + txt, 0, ln=1)
            self.set_text_color(0)
            self.ln()

    def lines(self):
        self.set_line_width(0.4)
        self.line(5.0, 5.0, 205.0, 5.0)  # top one
        self.line(5.0, 292.0, 205.0, 292.0)  # bottom one
        self.line(5.0, 5.0, 5.0, 292.0)  # left one
        self.line(205.0, 5.0, 205.0, 292.0)  # right one

    def print_chapter(self, num, title, name):
        self.chapter_title(num, title)
        self.chapter_body(num, name)


# metrices list of lists of elements ['name','num_series', 'num_repeats', 'id_próbki', 'num_of_values_external_factor', 'list_of_values_external_factor', 'metrice_id']
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
            for j in range(1, int(data[2]) + 1):
                cellPomiar = 'A' + str(row_counter - j)
                to_write = "pomiar " + str(int(data[2]) - j + 1)
                worksheet.write(cellPomiar, to_write, cell_format_blue)
                for b in range(0, len(data[5])):
                    cell = str(chr(ord('B') + b)) + str(row_counter - j)
                    worksheet.write(cell, "", unlocked)
    workbook.close()
    output.seek(0)

    filename = str(experiment_data[3]) + ".xlsx"
    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
    # else:
    # form = UploadFileForm()
    return HttpResponse(status=500)

@csrf_exempt
def get_user_number(request):
    response_data = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    username = body['username']
    users = []
    for l in list(User.objects.all()):
        users.append(l.username)
    nr = 0
    for x in range(len(users)):
        if username == users[x]:
            nr = x + 1
            break
    response_data['user_number'] = nr
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 200

    return response


def get_values_with_units(detailed_metric):
    external_factor = detailed_metric.sample.externalFactor.values.split(",")
    for ex in range(len(external_factor)):
        external_factor[ex] = external_factor[ex] + detailed_metric.sample.externalFactor.unit
    return external_factor


@csrf_exempt
def get_metrics_for_pdf(request):
    response_data = {}
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        id_exp = body['id']
        try:
            experiment = Experiment.objects.get(id=id_exp)
        except:
            response_data['message'] = 'Eksperyment nie istnieje'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)

        detailed_metrics_ids = []
        detailed_metrics_description = []
        metric_names = set()
        external_factor_names = set()
        supplements_names = set()

        for exp in experiment.detailedMetrics.all():
            text = exp.metric.name + " - " + exp.sample.externalFactor.name + " ( "
            for i in get_values_with_units(exp):
                text = text + i + " "
            text += ") "
            text += '\t' + exp.sample.supplement.get().name
            print(text)
            detailed_metrics_description.append(text)
            detailed_metrics_ids.append(exp.id)
            metric_names.add(exp.metric.name)
            external_factor_names.add(exp.sample.externalFactor.name)
            for sup in exp.sample.supplement.all():
                supplements_names.add(sup.name)

        response_data['metric_description'] = detailed_metrics_description
        response_data['metric_id'] = detailed_metrics_ids
        response_data['message'] = 'Pobrano metryki'
        response_data['metric_names'] = list(metric_names)
        response_data['external_factor_names'] = list(external_factor_names)
        response_data['supplements_names'] = list(supplements_names)
        response = HttpResponse(json.dumps(response_data))
        response.status_code = 200
    return response


@csrf_exempt
def generatePdf(request):

    response_data = {}
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    id_exp = body['idExp']
    id_plot = body['idPlots']
    info = body['info']

    metrics = body['metrics']
    ex_factors = body['ex_factors']
    supplements = body['supplements']
    id_detailed_metric = body['idDetailedMetrics']
    experiment = Experiment.objects.get(id=id_exp)
    users = []
    for l in list(User.objects.all()):
        users.append(l.username)

    global title
    title = experiment.name
    ch1 = 'Opis'
    ch2 = 'Receptura'
    ch3 = 'Mierzone cechy'
    ch4 = 'Tabele'
    ch5 = 'Wizualizacja'
    ch6 = 'Linki'

    pdf = PDF()
    pdf.set_author('Zespol 4')
    pdf.add_page()
    tmp = []
    suplements_ing = set()
    basic_ing = []

    my_body = json.dumps({'experiment_id': id_exp})
    my_body = my_body.encode(encoding='utf-8')
    my_url = 'http://localhost:8000/api/experiment/generateStats/'

    x = req.post(my_url, data=my_body)

    stats = json.loads(x.content)

    series_metric = stats['series_metric']
    mean_series = stats['mean_series']
    standard_devation = stats['standard_devation']

    for item in experiment.product.recipe.ingredients.all():
        tmp.append([item.basicIngredientBase.name, item.percentage])
    for item in experiment.detailedMetrics.all():
        for item2 in item.sample.supplement.all():
            suplements_ing.add(item2.name + " | zamiast: " + item2.basicIngredientBase.name)
    for x in tmp:
        basic_ing.append(str(x[0]) + " " + str(x[1]) + "%")

    plot_list = []
    metrics_names = set()
    metrics_id = set()
    over_tab = []  # insane power!!!
    for detailed_id in id_detailed_metric:
        detailed = experiment.detailedMetrics.get(id=detailed_id)
        result = Result.objects.filter(experiment=experiment, detailedMetric=detailed)
        tab = []
        for i in result:
            for x in range(i.detailedMetric.numberOfSeries):
                tmp1 = []
                for y in range(i.detailedMetric.numberOfRepeat):
                    tmp1.append("X")
                tab.append(tmp1)
            break

        for i in result:
            tab[i.numberOfSeries - 1][i.numberOfRepeat - 1] = i.value.split(",")

        metrics_name = ''
        external_factor = []
        for m in result:  # make it get more metric - take all an delete duplicates?
            metrics_name = m.detailedMetric.metric.name + " - " + m.detailedMetric.sample.supplement.get().name
            metrics_names.add(m.detailedMetric.metric.name)
            external_factor = get_values_with_units(m.detailedMetric)
            break
        mean = []
        devation = []
        for x in range(len(series_metric)):
            if series_metric[x][1] == detailed_id:
                mean.append(mean_series[x])
                devation.append(standard_devation[x])

        over_tab.append([metrics_name, external_factor, tab, mean, devation])

    # RadarPlot Make ------------------------------------------------------------------------
    if info[4] == True:
        sam = set()
        for ex in ex_factors:
            for dm in experiment.detailedMetrics.all():
                if (dm.sample.externalFactor.name == ex):
                    sam.add(dm.sample)
        sam = list(sam)

        sam_list = []
        sam_list.append([sam.pop(0)])

        while len(sam) > 0:
            x = sam.pop(0)
            for i in range(len(sam_list)):
                if sam_list[i][0].externalFactor.name == x.externalFactor.name:
                    sam_list[i].append(x)
                    continue
                if i + 1 == len(sam_list):
                    sam_list.append([x])

        sup_list = []
        for sup in sam_list:
            sup_list_2 = []
            for sup2 in sup:
                for s in sup2.supplement.all():
                    if s.name in supplements:
                        sup_list_2.append(sup2)
                        break
            sup_list.append(sup_list_2)

        sam_list = sup_list

        for x in range(len(sam_list)):
            for y in range(len(sam_list[x])):
                sam_list[x][y] = sam_list[x][y].id

        for x in range(len(sam_list)):
            figs = handle_radar_plot(id_exp, sam_list[x], metrics)
            for f in range(len(figs)):
                figs[f].set_size_inches(5, 5)
                figs[f].savefig('Radar_plot_nr_' + str(x) + str(f) + '.png')
                plot_list.append('Radar_plot_nr_' + str(x) + str(f) + '.png')

    # BarPLot Make -------------------------------------------------------------------------


    if info[5] == True:

        sam = set()
        for ex in ex_factors:
            for dm in experiment.detailedMetrics.all():
                if (dm.sample.externalFactor.name == ex):
                    sam.add(dm)
        sam_list = list(sam)



        sup_list = []
        for sup in sam_list:
            for s in sup.sample.supplement.all():
                if s.name in supplements:
                    sup_list.append(sup)
                    break
        sam = sup_list

        sam_list = [[sam.pop(0)]]

        while len(sam) > 0:
            x = sam.pop(0)
            for i in range(len(sam_list)):
                if sam_list[i][0].metric.name == x.metric.name and sam_list[i][0].sample.id == x.sample.id:
                    sam_list[i].append(x)
                    continue
                if i + 1 == len(sam_list):
                    sam_list.append([x])

        for x in range(len(sam_list)):
            for y in range(len(sam_list[x])):
                sam_list[x][y] = sam_list[x][y].id

        s_m = []
        for x in range(len(sam_list)):
            s_m2 = []
            for y in range(len(sam_list[x])):
                for z in range(experiment.detailedMetrics.get(id=sam_list[x][y]).numberOfSeries):
                    s_m2.append([z + 1, sam_list[x][y]])
            s_m.append(s_m2)

        for x in range(len(s_m)):
            body = {'series_metric': s_m[x]}

            figs = handle_bar_plot(stats, body)
            for f in range(len(figs)):
                figs[f].set_size_inches(5, 5)
                figs[f].savefig('Bar_plot_nr_' + str(x) + str(f) + '.png')
                plot_list.append('Bar_plot_nr_' + str(x) + str(f) + '.png')

    # LinearPLot Make -------------------------------------------------------------------------------------------------
    if info[6] == True:

        sam = set()
        for ex in ex_factors:
            for dm in experiment.detailedMetrics.all():
                if (dm.sample.externalFactor.name == ex):
                    sam.add(dm)
        sam_list = list(sam)

        sup_list = []
        for sup in sam_list:
            for s in sup.sample.supplement.all():
                if s.name in supplements:
                    sup_list.append(sup)
                    break
        sam = sup_list

        sam_list = [[sam.pop(0)]]

        while len(sam) > 0:
            x = sam.pop(0)
            for i in range(len(sam_list)):
                if sam_list[i][0].metric.name == x.metric.name and sam_list[i][0].sample.id == x.sample.id:
                    sam_list[i].append(x)
                    continue
                if i + 1 == len(sam_list):
                    sam_list.append([x])

        for x in range(len(sam_list)):
            for y in range(len(sam_list[x])):
                sam_list[x][y] = sam_list[x][y].id

        s_m = []
        for x in range(len(sam_list)):
            s_m2 = []
            for y in range(len(sam_list[x])):
                for z in range(experiment.detailedMetrics.get(id=sam_list[x][y]).numberOfSeries):
                    s_m2.append([z + 1, sam_list[x][y]])
            s_m.append(s_m2)

        for x in range(len(s_m)):
            body = {'series_metric': s_m[x]}

            figs = handle_linear_plot(stats, body)
            for f in range(len(figs)):
                figs[f].set_size_inches(5, 5)
                figs[f].savefig('Linear_plot_nr_' + str(x) + str(f) + '.png')
                plot_list.append('Linear_plot_nr_' + str(x) + str(f) + '.png')

    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVuB', '', 'DejaVuSansCondensed-BoldOblique.ttf', uni=True)

    pdf.set_font('DejaVu', '', 14)

    if info[0] == True:
        pdf.print_chapter(1, ch1, str(experiment.description) + "\n \n" + str(experiment.product.description))
    if info[1] == True:
        pdf.print_chapter(2, ch2, [basic_ing, list(suplements_ing)])
    if info[2] == True:
        pdf.print_chapter(3, ch3, metrics)
    if info[3] == True:
        pdf.print_chapter(6, ch6, [str(experiment.link)])
    if over_tab:
        pdf.print_chapter(4, ch4, over_tab)
    if plot_list:
        pdf.print_chapter(5, ch5, plot_list)

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askdirectory()
    pdf.output(file_path + '/Eksperyment.pdf', 'F')
    buffer = io.BytesIO()

    p = canvas.Canvas(buffer)

    p.drawString(100, 100, "Hello world.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

@csrf_exempt
def get_Experiment_and_author(request):

    for experiment in Experiment.objects:
        buffer = io.BytesIO()
        f.savefig(buffer)
        to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
        arr.append(to_return)

    v = json.dumps(dict({
        "plots": arr
    }))

    response = HttpResponse(content_type="application/json")
    response.write(v)
    return response

@csrf_exempt
def generateRadarPlots(request):
    # {
    #   experiment_id:__,
    #   samples:[_],
    #   metrics:[_]
    # }
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    arr = []
    figs = handle_radar_plot(body['experiment_id'], body['samples'], body['metrics'])
    #return figs
    for f in figs:
        buffer = io.BytesIO()
        f.savefig(buffer, format='png')

        to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
        arr.append(to_return)

    v = json.dumps(dict({
        "plots": arr
    }))

    response = HttpResponse(content_type="application/json")
    response.write(v)
    return response

    
@csrf_exempt
def generateBarPlots(request):
    #{
    #   experiment_id:__,
    #   series_metric:[[s1,m1], [s2,m2]]
    #}
    response = HttpResponse(content_type="application/json")
    v = ""
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        arr = []
        stats = json.loads(generateStats(request).content)
        figs = handle_bar_plot(stats,body)
        for f in figs:
                buffer = io.BytesIO()
                f.savefig(buffer, format='png')
                to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
                arr.append(to_return)

        v = json.dumps(dict({
            "message":"Plots generated",
            "plots": arr
        }))
        response.status_code=200
    else:
        v = json.dumps({
            "message": "Not POST method"
        })
        response.status_code=400

    response.write(v)
    return response
    
@csrf_exempt
def generateLinearPlots(request):
    #{
    #   experiment_id:__,
    #   series_metric:[[s1,m1], [s2,m2]]
    #}
    response = HttpResponse(content_type="application/json")
    v = ""
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        arr = []
        stats = json.loads(generateStats(request).content)
        figs = handle_bar_plot(stats, body)
        for f in figs:
            buffer = io.BytesIO()
            f.savefig(buffer, format='png')
            to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
            arr.append(to_return)

        v = json.dumps(dict({
            "message": "Plots generated",
            "plots": arr
        }))
        response.status_code = 200
    else:
        v = json.dumps({
            "message": "Not POST method"
        })
        response.status_code = 400

    response.write(v)
    return response


@csrf_exempt
def generateLinearPlots(request):
    # {
    #   experiment_id:__,
    #   series_metric:[[s1,m1], [s2,m2]]
    # }
    response = HttpResponse(content_type="application/json")
    v = ""
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        arr = []
        stats = json.loads(generateStats(request).content)
        figs = handle_linear_plot(stats, body)
        for f in figs:
            buffer = io.BytesIO()
            f.savefig(buffer, format='png')
            to_return = base64.encodebytes(buffer.getvalue()).decode('utf-8')
            arr.append(to_return)

        v = json.dumps(dict({
            "plots": arr
        }))
    else:
        v = json.dumps({
            "message": "Not POST method"
        })
        response.status_code = 400

    response.write(v)
    return response


@csrf_exempt
def generateStats(request):
    response_data = {}
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        name = body['experiment_id']
        try:
            experiment_results = Result.objects.filter(experiment_id=name)
        except:
            response_data['message'] = 'result nie istnieje'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        unique_series  = []
        series_metric = []
        unique_metric = []
        for i in range(len(experiment_results)):
            if [experiment_results[i].numberOfSeries,experiment_results[i].detailedMetric.id] not in series_metric:
                unique_series.append(experiment_results[i].numberOfSeries)
                series_metric.append([experiment_results[i].numberOfSeries,experiment_results[i].detailedMetric.id])
        values_series = {}
        for i in range(len(unique_series)):
            for j in range(len(experiment_results)):
                if unique_series[i] == experiment_results[j].numberOfSeries and series_metric[i][1] == experiment_results[j].detailedMetric.id:
                    splitted_values = experiment_results[j].value.split(',')
                    for s in range(len(splitted_values)):
                        splitted_values[s] = float(splitted_values[s])
                    if tuple(series_metric[i]) not in values_series:
                        values_series[tuple(series_metric[i])] = [len(splitted_values)]
                        values_series[tuple(series_metric[i])].extend(splitted_values)
                    else:
                        values_series[tuple(series_metric[i])].extend(splitted_values)
        if len(values_series.keys()) < 2:
            response_data['result'] = "brak odpowiedniej liczby wyników eksperymentu"
        else:
            mean_list, dev, all_test, bars = stats_data(values_series)

            response_data['result'] = "wykonano"
            response_data['mean_series'] = mean_list
            response_data['standard_devation'] = dev
            response_data['series_metric'] = series_metric
            response_data['test'] = all_test
            response_data['error_bars'] = bars
        response = HttpResponse(json.dumps(response_data))
        response.status_code = 200
        return response
    response_data['result'] = "not POST"
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return response

