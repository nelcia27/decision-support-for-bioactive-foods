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

def handle_radar_plot(experiment_id,sample_array):
    ef_set = set([])
    dm_res_dict = dict()
    samp_dict = dict()
    #pobranie rezultatów
    results = Result.objects.filter(experiment=experiment_id)
    samples = []
    #przefiltrowanie, czy próbki były pod wpływem jednego czynnika za pomocą ef_set
    for id in sample_array:
        s = Sample.objects.get(id=id)
        ef_set.add(s.externalFactor)
        samples.append(s)
        samp_dict[s.id]=[]
    if(len(ef_set)>1):
        raise AttributeError()
    ef = ExternalFactor.objects.get(name=ef_set.pop())
    #zebranie wyników o jednej metryce do jednej tablicy
    for r in results:
        try:
            dm_res_dict[str(r.detailedMetric)]
        except KeyError as identifier:
            dm_res_dict[str(r.detailedMetric)] = []
        dm_res_dict[str(r.detailedMetric)].append((r.numberOfRepeat,r.numberOfSeries, r.value.split(",")))
    keys = dm_res_dict.keys()
    #zredukowanie tablic do postaci próbka: [(metryka sz, tablica uśr. wyników)..]
    for k in keys:
        dm = DetailedMetrics.objects.get(id=k)
        if not(dm.sample.id in sample_array):
            continue
        val = ef.numberOfValues
        arr = np.zeros(val)
        for r in dm_res_dict[k]:
            for i in range(0,val):
                arr[i]+=float(r[2][i])
        s = dm.sample
        samp_dict[s.id].append((s,dm,arr/len(dm_res_dict[k])))
    keys = samp_dict.keys()
    val = ef.numberOfValues
    ret = []
    etiq= []
    ymax = 0
    x = 0
    for i in range(0,val):
        x = 0
        fig = plt.figure(figsize=(5,5))
        for k in keys:
            y = []
            etiq = []
            for r in samp_dict[k]:
                etiq.append(r[1].metric.name + " - "+r[1].metric.unit)
                y.append(r[2][i])
                if r[2][i] >ymax:
                    ymax = r[2][i]
            x = np.linspace(start=0,stop=360,num=len(etiq)) /180 * np.pi
            y+=y[:1]
            plt.polar(np.append(x,x[0]),y,'o-')
        plt.xticks(x,etiq)
        ret.append(fig)
    for f in ret:
        for ax in f.get_axes():
            ax.set_rticks(np.linspace(0,ymax,num=4))
    
    return ret