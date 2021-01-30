import xlrd
from .models import *
import io
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import statistics
from scipy.stats import kstest
from math import sqrt, trunc

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

def check_ef_samples(sample_array):
    ef_set = set([])
    for id in sample_array:
        s = Sample.objects.get(id=id)
        ef_set.add(s.externalFactor)
    if(len(ef_set)>1):
        raise AttributeError()
    ef = ef_set.pop()
    return ef

def handle_data_table(experiment_id,sample_array, m_array):
    dm_res_dict = dict()
    #pobranie rezultatów
    results = Result.objects.filter(experiment=experiment_id)
    #przefiltrowanie, czy próbki były pod wpływem jednego czynnika za pomocą ef_set
    check_ef_samples(sample_array)
    #zebranie wyników o jednej metryce do jednej tablicy
    for r in results:
        if not (r.detailedMetric.sample.id in sample_array and r.detailedMetric.metric.name in m_array):
            continue
        try:
            dm_res_dict[str(r.detailedMetric)]
        except KeyError as identifier:
            dm_res_dict[str(r.detailedMetric.id)] = []
        arr = []
        for a in r.value.split(","):
            arr.append(float(a))
        dm_res_dict[str(r.detailedMetric.id)].append((r.numberOfRepeat,r.numberOfSeries, arr))
    keys = dm_res_dict.keys()
    #wygenerowanie tablicy
    table = dict()
    for k in keys:
        dm = DetailedMetrics.objects.get(id=k)
        if not(dm.sample.id in sample_array):
            continue
        #nagłówek składa się z id próbki, danych o metryce, liczby serii i powtórzeń
        arr = []
        for r in dm_res_dict[k]:
            arr.append(r[2])
        try:
            table[str(dm.sample.id)].append(((dm.metric.name,dm.metric.unit), dm.numberOfSeries, dm.numberOfRepeat, arr))
        except KeyError as identifier:
            table[str(dm.sample.id)]=[((dm.metric.name,dm.metric.unit), dm.numberOfSeries, dm.numberOfRepeat, arr)]
    keys = table.keys()
    sortfunc = lambda x : x[0]
    dms = 0
    for k in keys:
        dms = len(table[k])
        break
    for k in keys:
        if (len(table[k])!=dms):
            raise AttributeError()
        table[k].sort(key=sortfunc)
    
    return table

def handle_bar_plot(table,body):
    sample_array = []
    met_set = set()
    for p in body['series_metric']:
        dm = DetailedMetrics.objects.get(id=p[1])
        sample_array.append(dm.sample.id)
        met_set.add(dm.metric)
    if (len(met_set)>1):
         raise AttributeError()
    ef = check_ef_samples(sample_array)
    val = []
    for v in ef.values.split(","):
        val.append(float(v))
    nval = len(val)
    width = val[0]*0.8/len(sample_array)
    axs = []
    to_return = []
    metric = met_set.pop()
    fig = plt.figure(figsize=(11,7))
    ax = fig.gca()
    ax.set_xticks(val)
    x = np.array(val)
    i = -len(sample_array)/2
    for b in body['series_metric']:
        ind = table['series_metric'].index(b)
        dm = DetailedMetrics.objects.get(id=b[1])
        data = table['mean_series'][ind]
        err = table['error_bars'][ind]
        line = ax.bar(x+i*width,data,yerr=err, width=width, align='edge')
        sup = dm.sample.supplement.all()
        lab = "Seria "+str(b[0])+" - "
        for s in sup:
            lab+=s.name+", "
        lab = lab[:(len(lab)-2)]
        line.set_label(lab)
        i+=1
    ax.set_ylabel(metric.name + " - " + metric.unit)
    ax.set_xlabel(ef.name + " - " + ef.unit)
    ax.legend()
    to_return.append(fig)
    
    return to_return

def handle_linear_plot(table,body):
    sample_array = []
    met_set = set()
    for p in body['series_metric']:
        dm = DetailedMetrics.objects.get(id=p[1])
        sample_array.append(dm.sample.id)
        met_set.add(dm.metric)
    if (len(met_set)>1):
        raise AttributeError()
    ef = check_ef_samples(sample_array)
    val = []
    for v in ef.values.split(","):
        val.append(float(v))
    nval = len(val)
    width = 1/len(sample_array)
    axs = []
    to_return = []
    metric = met_set.pop()
    fig = plt.figure(figsize=(11,7))
    ax = fig.gca()
    ax.set_xticks(val)
    x = np.array(val)
    for b in body['series_metric']:
        ind = table['series_metric'].index(b)
        dm = DetailedMetrics.objects.get(id=b[1])
        data = table['mean_series'][ind]
        err = table['error_bars'][ind]
        line = ax.errorbar(x,data,yerr=err)
        sup = dm.sample.supplement.all()
        lab = "Seria "+str(b[0])+" - "
        for s in sup:
            lab+=s.name+", "
        lab = lab[:(len(lab)-2)]
        line.set_label(lab)
        x+=width
    ax.set_ylabel(metric.name + " - " + metric.unit)
    ax.set_xlabel(ef.name + " - " + ef.unit)
    ax.legend()
    to_return.append(fig)
    
    return to_return

def handle_radar_plot(experiment_id,sample_array,m_array):
    table = handle_data_table(experiment_id,sample_array,m_array)
    ef = check_ef_samples(sample_array)
    keys = table.keys()
    nval = ef.numberOfValues
    val = ef.values.split(",")
    ret = []
    etiq = []
    ymax = 0
    x = 0
    met_max = dict()
    for k in keys:
        for v in table[k]:
            ymax = np.max(v[3])
            try:
                if ymax> met_max[v[0][0]]:
                    met_max[v[0][0]] = ymax
            except KeyError as i:
                met_max[v[0][0]] = ymax
    ymax = 0
    x = []
    for i in range(0,nval):
        fig = plt.figure(figsize=(11,7))
        for k in keys:
            etiq = []
            y = []
            for pack in table[k]:
                etiq.append(pack[0][0])
                arr = np.transpose(np.array(pack[3]))
                tmp = np.mean(arr[i])/met_max[pack[0][0]]
                y.append(tmp)
                if ymax < tmp:
                    ymax=tmp
            stop = 2*np.pi
            if len(etiq) == 2:
                stop = np.pi
            x = np.linspace(start=0,stop=stop,num=len(etiq),endpoint=False)
            y+=y[:1]
            pol = plt.polar(np.append(x,x[0]),y,'o-')
            sup = Sample.objects.get(id=k).supplement.all()
            lab = ""
            for s in sup:
                lab+=s.name+", "
            lab =lab[:(len(lab)-2)]
            pol[0].set_label(lab)
        plt.xticks(x,etiq)
        plt.title(ef.name+" ["+val[i]+" "+ef.unit+"]")
        ret.append(fig)
    rticks = np.linspace(0,ymax,num=4)
    for f in ret:
        for ax in f.get_axes():
            ax.set_rticks(rticks)
            ax.set_anchor('N')
            ax.legend(loc=8, ncol=int(len(keys)/5+1))
    return ret

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

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return trunc(number)

    factor = 10.0 ** decimals

    return trunc(float(number) * float(factor)) / float(factor)

