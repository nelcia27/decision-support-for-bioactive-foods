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
        table[str(dm.sample.id)].append(((dm.metric.name,dm.metric.unit), dm.numberOfSeries, dm.numberOfRepeat, arr))
    keys = table.keys()
    sortfunc = lambda x : x[0]
    for k in keys:
        table[k].sort(key=sortfunc)
    return table

def handle_bar_plot(experiment_id,sample_array,table):
    ef = check_ef_samples(sample_array)
    met_set = set()
    val = ef.values.split(",")
    axs = []
    to_return = []
    met_dict = dict()
    keys = table.keys()
    for k in keys:
        for v in table[k]:
            met_set.add(v[0][0]+ " - "+v[0][1])
    for met in met_set:
        met_dict[met]=[]
    for met in met_set:
        for k in keys:
            arr = []
            for v in table[k]:
                if v[0]==met:
                    arr.append(v[3])
            met_dict[met].append((k,arr))
    xticks = np.arange(0,len(val))
    width = 0.5/len(met_set)
    keys = met_dict.keys()
    for k in keys:
        fig, ax = plt.subplots(figsize=(9,6))
        ax.set_title(k)
        to_return.append(fig)
        axs.append(ax)
        ax.set_xticks(xticks)
        ax.set_xlabel(ef.name+" ["+ef.unit+"]")
        ax.set_xticklabels(val)
        i = 0
        for pair in met_dict[k]:
            tmp = np.transpose(np.array(pair[1]))
            yt = []

            for x in xticks:
                yt.append(np.mean(tmp[x]))
            bar_sub =ax.bar(xticks+i*width,yt,align='edge',width=width)
            sup = Sample.objects.get(id=pair[0]).supplement.all()
            lab = ""
            for s in sup:
                lab+=s.name+", "
            lab =lab[:(len(lab)-2)]
            bar_sub.set_label(lab)
            i+=1
        ax.legend()
    return to_return

def handle_linear_plot(experiment_id,sample_array, m_array):
    dm_res_dict = dict()
    to_return=[]
    #pobranie rezultatów
    results = Result.objects.filter(experiment=experiment_id)
    #przefiltrowanie, czy próbki były pod wpływem jednego czynnika za pomocą ef_set
    ef = check_ef_samples(sample_array)
    #zebranie wyników o jednej metryce do jednej tablicy
    for r in results:
        if not (r.detailedMetric.sample.id in sample_array and r.detailedMetric.metric.name in m_array) :
            continue
        try:
            dm_res_dict[str(r.detailedMetric.id)]
        except KeyError as identifier:
            dm_res_dict[str(r.detailedMetric.id)] = []
        arr = []
        for r in r.value.split(','):
            arr.append(r[2])
        dm_res_dict[str(r.detailedMetric.id)].append((r.numberOfRepeat,r.numberOfSeries, arr))
    keys = dm_res_dict.keys()
    met_res_dict = dict()
    for m in m_array:
        met_res_dict[m] = []
    for k in keys:
        dm = DetailedMetrics.objects.get(id=k)
        ser_dict = dict()
        for i in range(1,dm.numberOfSeries+1):
            ser_dict[i] = []
        for v in dm_res_dict[k]:
            ser_dict[v[1]].append(v[2])
        met_res_dict[dm.metric.name].append((dm.sample,ser_dict))
    xTemplate = [] 
    for v in ef.values.split(","):
        xTemplate.append(float(v))
    for m in m_array:
        fig, ax = plt.subplots(figsize=(7,7))
        for p in met_res_dict[m]:
            series = p[1].keys()
            ydata = []
            xdata = []
            for s in series:
                ydata.append(p[1][s])
                xdata.append(xTemplate)
            lines = ax.plot(np.array(xdata).transpose(),np.array(ydata).transpose(), marker="o")
            sup = p[0].supplement.all()
            lab = ""
            for s in sup:
                lab+=s.name+", "
            lab =lab[:(len(lab)-2)]
            for s in series:
                lines[s].set_label("Seria "+str(s)+" - "+lab)
        ax.legend()
        to_return.append(fig)
    return to_return


def handle_radar_plot(experiment_id,sample_array,table):
    ef = check_ef_samples(sample_array)
    keys = table.keys()
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
                etiq.append(pack[0][0]+" - "+pack[0][1])
                arr = np.transpose(np.array(pack[3]))
                vmax=np.max()
                tmp = np.mean(arr[i])/vmax
                y.append(tmp)
                if ymax < tmp:
                    ymax=tmp
            x = np.linspace(start=0,stop=2*np.pi,num=len(etiq)) /180 * np.pi
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
    rticks = np.linspace(0,ymax,num=int(ymax))
    for f in ret:
        for ax in f.get_axes():
            ax.set_rticks(rticks)
            ax.set_anchor('N')
            ax.legend(loc=8, ncol=len(keys)/5+1)
    return ret