import xlrd
from .models import *
import statistics
from scipy.stats import kstest
from math import sqrt

def handle_experiment_data(file):
    wb = xlrd.open_workbook(file_contents=file.read())
    result = []
    experimentId = None
    for sheet in wb.sheets():
        data = str(sheet.name).split(",")
        if len(data) > 1:
            res = []
            res.append(data[2])
            infos = DetailedMetrics.objects.get(id=data[2])
            series = []
            sample = Sample.objects.get(id=data[0])
            external_factor = ExternalFactor.objects.get(name=sample.externalFactor)
            rowcounter = 3
            colcounter = 1
            for i in range(0, infos.numberOfSeries):
                serie = []
                for j in range(0, infos.numberOfRepeat):
                    measure = ""
                    if j != 0:
                        rowcounter = rowcounter + 1
                    for k in range(0, external_factor.numberOfValues):
                        if measure == "":
                            measure = measure + str(sheet.cell_value(rowx=rowcounter, colx=colcounter + k))
                        else:
                            measure = measure + "," + str(sheet.cell_value(rowx=rowcounter, colx=colcounter + k))
                    serie.append(measure)
                rowcounter = rowcounter + 2
                series.append(serie)
            res.append(series)
            result.append(res)
        else:
            experimentName = sheet.cell_value(rowx=0, colx=0)
            experimentAuthor = sheet.cell_value(rowx=3, colx=0)
            experiment = Experiment.objects.get(name=experimentName, author_id=experimentAuthor)
            experimentId = experiment.id

    #wstawienie wyników do bazy
    for res in result:
        for i in range(0, len(res[1])):
            for j in range(0, len(res[1][i])):
                if experimentId:
                    r = Result(value=res[1][i][j], numberOfRepeat=j + 1, numberOfSeries=i + 1, detailedMetric_id=res[0], experiment_id=experimentId)
                    r.save()

def stats_data(data):
    all_values = []
    for key in data.keys():
        value_inside = [[] for i in range(data[key][0])]
        lista = data[key]
        for i in range(1,len(lista)):
            value_inside[(i-1)%data[key][0]].append(lista[i])
        all_values.append(value_inside)
    mean_list = [[] for key in data.keys()]
    dx = [[] for key in data.keys()]
    test_values = [[] for key in data.keys()]
    bars = [[] for key in data.keys()]
    for i in range(len(all_values)):
        for j in range(len(all_values[i])):
            test_values[i].append(kstest(all_values[i][j], 'norm'))
            mean = sum(all_values[i][j])/len(all_values[i][j])
            deviation = statistics.stdev(all_values[i][j])
            mean_list[i].append(mean)
            dx[i].append(deviation)
            bars[i].append(deviation/sqrt(len(all_values[i][j])))

    return mean_list,dx,test_values,bars

