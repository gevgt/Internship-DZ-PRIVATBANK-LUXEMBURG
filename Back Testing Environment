import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import spearmanr
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning) #!!!


###############################################################################
############################## Update-Protokoll ###############################
###############################################################################

#Update (30.03.2020): Korrektur, es wird nun vor der Berechnung der Kennzahlen 
#dafür gesorgt, dass benchmark und pf den gleichen Start- und Endpunkt haben.

#Update (28.03.2020): Kommentare und Layout bei rang_korrelation()

#Update (26.03.2020): Kommentare und Layout bei kennzahlen()

###############################################################################
###############################################################################
###############################################################################




    
def kennzahlen(x, pf, start="2002-02-14", bm=False):
    '''
    Parameters
    ----------
    x : DATAFRAME
        Für Berechnung der Benchmark - Gleichgewichtung der Titel.
    pf : DATAFRAME
        Performance der zu testenden Strategie (bereits in anderem Makro errechnet). Index und keine Returns
    start : STRING , optional
        Start-Date der Kennzahlenerstellung. The default is "2002-02-14".
    bm : DATAFRAME, optional
        DESCRIPTION. The default is False.
    bm_eigene : BOOLEAN, optional
        DESCRIPTION. The default is None. Wenn vorhanden, setze auf TRUE
    Returns
    -------
    '''
    
    
    ###########################################################################
    ####################### Vorbereitung der Zeitreihen #######################
    ###########################################################################    
    
    #Startdatum in datetime Format umwandeln und die pf Zeitreihe entsprechend
    #beschneiden
    start = pd.to_datetime(start, format="%Y-%m-%d")
    pf = pf[:][start:]
    
    
    #Normalisieren, indem die Zeitreihe durch den Startwert geteilt werden
    dates = list(pf.index)
    pf = pf.values / pf.values[0]
    pf = pd.DataFrame(pf, index=dates)
    
    
    #Erstellung einer Benchmark. Wenn bm==False, wird aus dem ursprünglichem
    #Datenset eine Benchmark erstellt, welche aus allen Titeln besteht, die
    #gleichgewichtet in die Performance einfließen.
    #Wenn bm!=False ist heißt das, man hat eine eigene Benchmark in die 
    #Funktion gegeben. Der Input muss also eine nx1 Zeitreihe sein.
    try:       
        if bm == False:
            #Durchschnitt Returns aus jede Zeile. Wichtig ist, das x Preise
            #beinhaltet und keine returns.
            benchmark2 = np.nanmean(np.array(x.values[1:]/x.values[:-1], 
                                             dtype=float), axis=1)
            
            #Die Returns werden geometrisch verknüpft, um eine Zeitreihe zu
            #erstellen
            g = np.array([1])
            for i in range(benchmark2.shape[0]):
                g = np.append(g, benchmark2[i]*g[-1])
            benchmark = pd.DataFrame(g.reshape(g.shape[0],1),index=x.index)
            
            #Die Benchmark wird gekürzt und normalisiert.
            benchmark = benchmark[:][start:]
            benchmark = pd.DataFrame(benchmark.values/benchmark.values[0], 
                                     index=benchmark.index)
    except:
        #Check, ob Input eine Zeitreihe ist.
        if len(bm) > 1:
            #Kürzen und Normalisieren.
            benchmark = bm[:][start:]
            benchmark = pd.DataFrame(benchmark.values/benchmark.values[0], 
                                     index=benchmark.index)    
        
    
    
    #Die Frequenz bestimmen. Also ob Tages-, Wochen- oder Monatsdaten 
    #vorliegen.
    #delta ist der Abstand zwischen zwei Punkten
    delta = (benchmark.index[1] - benchmark.index[0]).days
    if delta < 5:
        frequenz = "täglich"
        fqnz = 250
    elif delta > 5 and delta < 20:
        frequenz = "wöchentlich"
        fqnz = 50
    else:
        frequenz = "monatlich"
        fqnz = 12
        
        
        
    #pf und benchmark auf eine Länge trimmen, da es sein kann, dass eine Zeit-
    #reihe akuteller ist als die andere und deshalb unterschiedlich lang.
    if len(pf) > len(benchmark):
        diff = len(benchmark) - len(pf)
        pf = pf.iloc[:diff]
    elif len(benchmark) > len(pf):
        diff = len(pf) - len(benchmark)
        benchmark = benchmark.iloc[:diff]
    
    
    
    
    
    ###########################################################################
    ############################### Kennzahlen ################################
    ###########################################################################    
    
    #Berechnung der Kennzahlen, die in liste eingetragen werden (wird als
    #Matrix mit einsen initialisiert). In der ersten Runde werden die Kenn-
    #zahlen der Strategie berechnet und in der zweiten Runde die der Benchmark-
    liste = np.ones((11,1))
    for z in [pf, benchmark]:
        
        #Returns
        pf_return = z.values[1:]/z.values[:-1]
        
        #!!! Kummulierte, aggrigierte, geometrische Returns.
        cagr = z.values[-1] ** (1/(z.shape[0]/fqnz)) - 1
        
        #Standardabweichung
        std = np.nanstd(pf_return) * (fqnz**0.5)
        
        #Scharpe Ratio
        sharpe = np.round(cagr / std, 2)
        
        
        
        #Beste und schlechteste Monatsrendite: Dazu wird aus dem Datum die
        #Monatsnummer gemacht um einen Start und Endwert zu erhalten, wenn die
        #Monatsnummer umspringt.
        dates = [d.month for d in pf.index]
        z2 = z.values
        s = dates[0]
        s_value = z2[0]
        month_r = np.array([])
        
        for i in range(1, z2.shape[0]):
            try:
                if dates[i] != s:
                    month_r = np.append(month_r, z2[i]/s_value-1)
                    s = dates[i]
                    s_value = z2[i]
            except:
                break
                
        best_month = np.round(np.nanmax(month_r), 3) * 100
        worst_month = np.round(np.nanmin(month_r), 3) * 100
        
        
        
        #Profitable Monate: Überall wo die Returns größer als 0 sind, wird eine
        #1 vergeben und sonst 0. Das ganze wird dann aufsummiert und ergibt
        #dann die Anzahlt der Monate mit positiven Returns.
        pos_month = np.where(month_r > 0, 1, 0)
        p_profitable = np.round(np.nansum(pos_month) / 
                                pos_month.shape[0], 3) * 100
        
        
                                
        #Downside Deviation: Positive Returns werden ersetzt und die Standard-
        #abweichung ermittelt. Dann wird das Ganze annualisiert und in Prozent
        #umgeformt.
        down_dev = np.round(np.nanstd(np.where(pf_return < 1, pf_return-1, 
                                np.nan)) * (fqnz**0.5), 3) * 100

        
                                               
        #Value at Risk und Expected Shortfall: Die Returns bilden und dann sor-
        #tieren. Als VaR wird dann das (len(var)*0.01-1)-te Element genommen.
        r = z.values[1:]/z.values[:-1] -1
        var = np.sort(r, axis=0)
        es = np.round(np.nanmean(var[:int(var.shape[0]*0.01)]), 3) * 100
        var = np.round(float(var[int(var.shape[0]*0.01)-1]), 3) * 100
        
        #Annualisierung von var und es.
        if frequenz=="wöchentlich":
            var = var
            es = es
        elif frequenz=="täglich":
            var = var*5
            es = es*5
        elif frequenz=="monatlich":
            var = var/4
            es = es/4
        
        
        
        #Sortino Ratio: Alle positiven returns werden durch 0 ersetzt. Der Vek-
        #tor wird dann aufsummiert, durch n dividiert, die Wurzel gezogen und
        #annualisiert.
        variance = ((np.nansum(np.where(pf_return < 1, (pf_return-1)**2, 0)) / 
                     pf_return.shape[0]) ** 0.5) * (fqnz**0.5)
        sortino = np.round(cagr / variance, 2)

        
        
        #Maximum Drawdown: Größter Kursverlust vom Höchst- zum Tiefststand. 
        #Geht jeden Tag durch und berechnet die Rendite zum tiefsten Punkt, der
        #nach dem Betrachtungszeitpunkt folgt.
        max = 1000
        for i in range(z.shape[0]):
            try:
                dd = np.min(z.values[i+1:]) / z.values[i] - 1
                if dd < max:
                    max = dd
            except:
                break
        max_dd = np.round(max, 3) * 100
        
        
        
        #In Prozentzahlen umformen.
        cagr = np.round(cagr, 3) * 100
        std = np.round(std, 3) * 100
        
        
        
        #Alles in einen Array einordnen
        performance = np.array([cagr[0], std, down_dev, var, es, sharpe[0], 
                sortino[0], max_dd[0], worst_month, best_month, p_profitable])
        
    
    
        #Matrix mit den beiden Arrays, dem der Strategie und dem der Benchmark.
        liste = np.concatenate([liste, performance.reshape(11,1)], axis=1)
    
    
    
    
    
    ###########################################################################
    ############################# Excess Returns ##############################
    ###########################################################################


     
        
        
    #Liste mit nur den Jahreszahlen
    years = list(pf.index.year)
    
    #Startwerte
    s = years[0]
    s_index = 0
    
    #Zu füllende Arrays
    r_strategie_v = np.array([])
    r_benchmark_v = np.array([])
    m_dates = []

    #Es wird der Return über jeweils ein Jahr bestimmt, beginnend am 01.01.
    #und endend am 31.12.
    for i in range(len(years)):
        #Wenn das Jahr wechselt, wird der der Return für das jeweilige Jahr
        #ermittelt für beide Zeitreihen.
        if years[i] != s:                
            r_strategie_v = np.append(r_strategie_v, pf.iloc[i-1] / 
                                      pf.iloc[s_index] - 1)
            r_benchmark_v = np.append(r_benchmark_v, benchmark.iloc[i] / 
                                      benchmark.iloc[s_index] - 1)        
            m_dates.append(years[i-1])
            s_index = i-1
            s = years[i]
            
        #Der letzte Eintrag ist automatisch das Enddatum des Jahres.    
        elif i == len(years)-1:
            r_strategie_v = np.append(r_strategie_v, pf.iloc[i] / 
                                      pf.iloc[s_index] - 1)
            r_benchmark_v = np.append(r_benchmark_v, benchmark.iloc[i] / 
                                      benchmark.iloc[s_index] - 1)
            m_dates.append(years[i])
            
    #Erstellen von DataFrames
    r_strategie = pd.DataFrame(r_strategie_v, index=m_dates)
    r_benchmark = pd.DataFrame(r_benchmark_v, index=m_dates)
    
    
    
    #Excess Return
    diff = r_strategie - r_benchmark
    
    #Da diff.shape[0] ist gleich der Anzahl der Jahre. Nun wird ein Array
    #erstellt der genauso lang ist wie pf. Bei Wochendaten: Für jede Woche wird
    #der Excess Return des jeweiligen Jahres eingetragen.
    diff_ts = np.array([])
    for i in range(pf.shape[0]):
        diff_ts = np.append(diff_ts, diff.loc[pf.index.year[i]])
    diff_ts = pd.DataFrame(diff_ts, index=pf.index)





    ###########################################################################
    ################################# Output ##################################
    ###########################################################################
    
    #Grafik
    fig, ax1 = plt.subplots()
    
    #1. Achse
    ax1.grid(color='grey', linestyle='-', linewidth=0.1)
    ax1.plot(pf-1, zorder=3)
    ax1.plot(benchmark-1, zorder=2)
    ax1.legend(["Strategie", "Benchmark"])
    ax1.set_xlabel("t")
    ax1.set_ylabel("returns (in 100%)")    
    
    #2. Achse
    ax2 = ax1.twinx()
    ax2.plot(diff_ts, linewidth=0.5, color="green")
    ax2.set_ylabel("excess returns")
    ax1.set_zorder(2)
    ax1.patch.set_visible(False)
    
    
    #DataFrame mit den Kennzahlen der beiden Zeitreihen
    zeilen = np.array(["CAGR p.a. (%)", "Standard Deviation (%)", 
        "Downside Deviation (%)", "99% VaR für 1 Woche (%)", 
        "Expected Shortfall (%)", "Sharpe Ratio", "Sortino Ratio", 
        "Maximum Drawdown (%)", "Worst Month´s Return (%)", 
        "Best Month´s Return (%)", "Profitable Months (%)"])
    spalten = np.array(["Strategie", "Benchmark"])
    knz = pd.DataFrame(liste[:,1:], columns=spalten, index=zeilen)
    print("Start: " + str(str(start)[:10]))
    print("Ende:  " + str(str(pf.index[-1])[:10]))
    print("Frequenz: " + str(frequenz) + "\n")
    print(knz)
    
    fig.savefig("Backtest.pdf", bbox_inches='tight')    
    plt.show()
    
    return knz










#prices: DataFrame mit den Schlusskursen aller Assets zu jedem Zeitpunkt
#rank: DataFram mit dem Rang jedes Assets zu jedem Zeitpunkt
#window: Scalar, mit wie viele Zeiteinheiten in der Zukunft man den heutigen 
#Rang in bezug setzt
def rang_korrelation(prices, rank, window=48):
    prices = prices.values
    rank = rank.values
    
    #Es gibt 5 Quantile, die jeweils 20% beinhalten.
    v_02 = np.ones((1,2))
    v_04 = np.ones((1,2))
    v_06 = np.ones((1,2))
    v_08 = np.ones((1,2))
    v_10 = np.ones((1,2))
    
    
    for i in range(window, rank.shape[0]):
        #m = 
        #r = 
        m_02 = np.array([])
        r_02 = np.array([])
        m_04 = np.array([])
        r_04 = np.array([])
        m_06 = np.array([])
        r_06 = np.array([])
        m_08 = np.array([])
        r_08 = np.array([])
        m_10 = np.array([])
        r_10 = np.array([])    
        
        for j in range(rank.shape[1]):
            
            #Check, ob der Preis und Rang eines Assets vor window ZE verfügbar
            #war und der Preis heute immer auch Verfügbar ist, um die Kor-
            #relation zwischen dem Rang vor window ZE und heute herzustellen.
            if (    np.isnan(rank[i-window,j])==0 
                and np.isnan(prices[i-window,j])==0 
                and np.isnan(prices[i,j])==0
                ):
                
                #Returns und Ränge in die jeweiligen Quantile einordnen.
                if rank[i-window, j] < np.nanmax(rank[i-window])*0.2:
                    m_02 = np.append(m_02, rank[i-window, j])
                    r_02 = np.append(r_02, prices[i,j]/prices[i-window,j])
                elif (    rank[i-window, j] >= np.nanmax(rank[i-window])*0.2 
                      and rank[i-window, j] < np.nanmax(rank[i-window])*0.4
                      ):
                    m_04 = np.append(m_04, rank[i-window, j])
                    r_04 = np.append(r_04, prices[i,j]/prices[i-window,j])
                elif (    rank[i-window, j] >= np.nanmax(rank[i-window])*0.4 
                      and rank[i-window, j] < np.nanmax(rank[i-window])*0.6
                      ):
                    m_06 = np.append(m_06, rank[i-window, j])
                    r_06 = np.append(r_06, prices[i,j]/prices[i-window,j])
                elif (    rank[i-window, j] >= np.nanmax(rank[i-window])*0.6 
                      and rank[i-window, j] < np.nanmax(rank[i-window])*0.8
                      ):
                    m_08 = np.append(m_08, rank[i-window, j])
                    r_08 = np.append(r_08, prices[i,j]/prices[i-window,j])
                else:
                    m_10 = np.append(m_10, rank[i-window, j])
                    r_10 = np.append(r_10, prices[i,j]/prices[i-window,j])
        
        
        #Die Rangkorrelation zwischen dem damaligen Rang und dem heutigen. Der
        #heutige Rang beruht auf der Rendite von damals (vor windows ZE) bis
        #heute.
        v_02 = np.concatenate((v_02, np.round(np.array(spearmanr(m_02, r_02)),
                                              4).reshape(1,2)), axis=0)
        v_04 = np.concatenate((v_04, np.round(np.array(spearmanr(m_04, r_04)),
                                              4).reshape(1,2)), axis=0)
        v_06 = np.concatenate((v_06, np.round(np.array(spearmanr(m_06, r_06)),
                                              4).reshape(1,2)), axis=0)
        v_08 = np.concatenate((v_08, np.round(np.array(spearmanr(m_08, r_08)),
                                              4).reshape(1,2)), axis=0)
        v_10 = np.concatenate((v_10, np.round(np.array(spearmanr(m_10, r_10)),
                                              4).reshape(1,2)), axis=0)
    
    
    
    #Erstellen eines DataFrames welcher als Output ausgegeben wird.    
    matrix = np.array([np.round(np.mean(v_02, axis=0),4),
                       np.round(np.mean(v_04, axis=0),4),
                       np.round(np.mean(v_06, axis=0),4),
                       np.round(np.mean(v_08, axis=0),4),
                       np.round(np.mean(v_10, axis=0),4)])
    
    rk = pd.DataFrame(matrix, columns=["Rho", "p-Wert"], 
                index=[" 0%-20%", "20%-40%", "40%-60%", "60%-80%", "80%-100%"])
    
    print(rk)
    
    return rk
