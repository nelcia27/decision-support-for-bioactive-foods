import xlrd
from .models import *
import io
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
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

def handle_data_table(experiment_id,sample_array):
    ef_set = set([])
    dm_res_dict = dict()
    table = dict()
    #pobranie rezultatów
    results = Result.objects.filter(experiment=experiment_id)
    samples = []
    #przefiltrowanie, czy próbki były pod wpływem jednego czynnika za pomocą ef_set
    for id in sample_array:
        s = Sample.objects.get(id=id)
        ef_set.add(s.externalFactor)
        samples.append(s)
        table[str(s.id)] = []
    if(len(ef_set)>1):
        raise AttributeError()
    #zebranie wyników o jednej metryce do jednej tablicy
    for r in results:
        try:
            dm_res_dict[str(r.detailedMetric)]
        except KeyError as identifier:
            dm_res_dict[str(r.detailedMetric.id)] = []
        dm_res_dict[str(r.detailedMetric.id)].append((r.numberOfRepeat,r.numberOfSeries, r.value.split(",")))
    keys = dm_res_dict.keys()
    #wygenerowanie tablicy
    for k in keys:
        dm = DetailedMetrics.objects.get(id=k)
        if not(dm.sample.id in sample_array):
            continue
        #nagłówek składa się z id próbki, danych o metryce, liczby serii i powtórzeń
        arr = []
        for r in dm_res_dict[k]:
            arr_in = []
            for n in r[2]:
                arr_in.append(float(n))
            arr.append(arr_in)
        table[str(dm.sample.id)].append((dm.metric.name+" - "+dm.metric.unit, dm.numberOfSeries, dm.numberOfRepeat, arr))
    keys = table.keys()
    sortfunc = lambda x : x[0]
    for k in keys:
        table[k].sort(key=sortfunc)
    return table

def handle_bar_plot(experiment_id,sample_array,table):
    to_return = []
    return to_return

def handle_linear_plot(experiment_id,sample_array,table):
    to_return = []
    return to_return


def handle_radar_plot(experiment_id,sample_array,table):
    #sprawdzenie czy próbki są z jednego czynnika zewnętrznego
    ef_set = set([])
    for id in sample_array:
        s = Sample.objects.get(id=id)
        ef_set.add(s.externalFactor)
    if(len(ef_set)>1):
        raise AttributeError()
    #pobranie "czystej tabeli" z danymi
    table = handle_data_table(experiment_id,sample_array)
    keys = table.keys()
    ef = ef_set.pop()
    nval = ef.numberOfValues
    val = ef.values.split(",")
    ret = []
    ymax = 0
    x = 0
    for i in range(0,nval):
        x = 0
        fig = plt.figure(figsize=(7,7))
        for k in keys:
            etiq = []
            y = []
            for pack in table[k]:
                etiq.append(pack[0])
                tmp = np.mean(np.transpose(np.array(pack[3]))[i])
                y.append(tmp)
                if ymax < tmp:
                    ymax=tmp
            x = np.linspace(start=0,stop=360,num=len(etiq)) /180 * np.pi
            y+=y[:1]
            pol = plt.polar(np.append(x,x[0]),y,'o-')
            pol[0].set_label("Próbka "+k)
        plt.xticks(x,etiq)
        plt.title(ef.name+" ["+val[i]+" "+ef.unit+"]")
        ret.append(fig)
    rticks = np.linspace(0,ymax,num=int(ymax))
    for f in ret:
        for ax in f.get_axes():
            ax.set_rticks(rticks)
            ax.set_anchor('N')
            ax.legend(loc=8, ncol=len(keys)/5+1)
    return ret