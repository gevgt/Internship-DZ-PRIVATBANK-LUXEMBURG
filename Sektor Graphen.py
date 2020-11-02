import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns; sns.set()
from scipy.stats import rankdata

###############################################################################
################################### Mining ####################################
###############################################################################
def miningreuters(x):
    
    #Lädt die gewünschten Daten und entpackt sie.
    #Gibt die Matrix mit den Preisen und Datums Vektor aus.
    
    x = np.array(x.values, dtype=str)
    dates = x[:,0]
    x = np.array(x[:,1:], dtype=float)
    
    return x, dates


###############################################################################
############################### Relative Stärke ###############################
###############################################################################
def rs(x, dates, pp, t_chart):    


    #String Format in Datums Format
    d = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
    date = d[-1]

    #Finde den Index des Datums vor 10 und 2 Jahren um das Datenset zu kürzen.
    
    #Datum vor genau 10 und 2 Jahren bestimmen
    c_date10 = dt.date(date.year -10, date.month, date.day)
    c_date2 = dt.date(date.year -2, date.month, date.day)
    
    #Arrays definieren, die mit den Tagen vor und nach dem Stichtag gefüllt
    #werden, da es sein kann, dass der Stichtag z.B. an einem Samstag ist und
    #somit keine Preis Daten verfügbar sind. Umständlich gemacht, gerne
    #nachbessern!
    c_dates10 = np.array([])
    c_dates2 = np.array([])
    
    tage = 1 # Änderung 01.03.2020
    for i in range(-1, 2):
        try:
            c_dates10 = np.append(c_dates10, dt.date(c_date10.year, 
                                            c_date10.month, c_date10.day + i))
            c_dates2 = np.append(c_dates2, dt.date(c_date2.year, c_date2.month, 
                                                             c_date2.day + i))
        except:
            c_dates10 = np.append(c_dates10, dt.date(c_date10.year, 
                                                     c_date10.month+1, tage))
            c_dates2 = np.append(c_dates2, dt.date(c_date2.year, 
                                                   c_date2.month+1, tage))
            tage +=1
            
        
    gefunden = False
    for i in range(dates.shape[0]):
        if d[i] in c_dates10:
            idx10 = - (dates.shape[0] - i)
            gefunden = True
            break
    
    for i in range(dates.shape[0]):
        if d[i] in c_dates2:
            idx2 = - (dates.shape[0] - i)
            break
    
    if gefunden == False:
        #Wenn das Datenset zu kurz ist müssen noch 200 Tage abgezogen werden,
        #da noch zusätzlich 200 Tage für den ersten Moving Average Eintrag 
        #benötigt werden
        idx10 = - (dates.shape[0]-200)
    
    
    #Datumsvektor beschneiden
    
    #Short Term
    sdates = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates[idx2:]]
    #Long Term
    ldates = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates[idx10:]]

    

    ############################# Relative Stärke #############################
    
    #Relative Stärke, Punkt der Standardisierung -2 Jahre, also idx2 
    #(Short Term)
    rss = (x/x[idx2]) / (x[:,0]/x[idx2,0]).reshape(x.shape[0],1)
    rss = rss[:,1:]
    
    #Relative Stärke, Punkt der Standardisierung -10 Jahre, also idx10
    #(Long Term)
    rsl = (x/x[idx10]) / (x[:,0]/x[idx10,0]).reshape(x.shape[0],1)
    rsl = rsl[:,1:]
    
    
    #Für den 10-Jahre-Chart: nur 200 MA, da andere zu kurzfristig
    #Für den 2-Jahre-Chart: 20, 50 und 200 MA
    
    #20 Tage Moving Average
    sma_20s = np.ones((1, rss.shape[1]))
    for i in range(20, x.shape[0]+1):
        mas = np.nanmean(rss[i-20:i], axis=0)
        sma_20s = np.concatenate((sma_20s, mas.reshape(1, mas.shape[0])), 
                                 axis=0)
    sma_20s = sma_20s[idx2:]

    #50 Tage Moving Average
    sma_50s = np.ones((1, rss.shape[1]))
    for i in range(50, x.shape[0]+1):
        mas = np.nanmean(rss[i-50:i], axis=0)
        sma_50s = np.concatenate((sma_50s, mas.reshape(1, mas.shape[0])), 
                                 axis=0)
    sma_50s = sma_50s[idx2:]
    
    #200 Tage Moving Average
    sma_200s = np.ones((1, rss.shape[1]))
    sma_200l = np.ones((1, rss.shape[1]))
    for i in range(200, x.shape[0]+1):
        mas = np.nanmean(rss[i-200:i], axis=0)
        sma_200s = np.concatenate((sma_200s, mas.reshape(1, mas.shape[0])), 
                                  axis=0)
        mal = np.nanmean(rsl[i-200:i], axis=0)
        sma_200l = np.concatenate((sma_200l, mal.reshape(1, mas.shape[0])), 
                                  axis=0)
    sma_200s = sma_200s[idx2:]
    sma_200l = sma_200l[idx10:]
    
    #Return Vektoren müssen die gleiche Länge haben wie die MA Vektoren
    rss = rss[idx2:]
    rsl = rsl[idx10:]
    
    ################################# Charts ##################################
    
    for i in range(rss.shape[1]):
        #Oberer Chart
        plt.subplot(211)
        plt.plot(sdates, rss[:,i])
        plt.plot(sdates, sma_20s[:,i], color="red", linewidth=0.5)
        plt.plot(sdates, sma_50s[:,i], color="green", linewidth=0.5)
        plt.plot(sdates, sma_200s[:,i], color="orange", linewidth=0.5)
        plt.xticks(fontsize=8, rotation=10)
        #Erinnerung: Benchmark ist in Spalte 0!!!
        plt.title(str(t_chart[i+1]) + " relativ zum " + str(t_chart[0] + " (" 
                  + str(ldates[-1]) + ")"), fontsize=12, fontweight="bold")
        plt.legend(["Relative Strength", "Moving Average 20d", 
                    "Moving Average 50d", "Moving Average 200d"], loc=0, 
                    fontsize="xx-small")
        
        #Unterer Chart
        plt.subplot(212)
        plt.plot(ldates, rsl[:,i])
        plt.plot(ldates, sma_200l[:,i], color="orange", linewidth=0.5)
        plt.xticks(fontsize=8, rotation=10)
        
        #Speichern und "show", damit nicht alle Graphen in ein Chart geplottet
        #werden
        pp.savefig(bbox_inches='tight')
        plt.show()

 
 
    

###############################################################################
############################## Relative Rotation ##############################
###############################################################################    
def relative_rotation(x, dates, datei_name, t_chart, frequency="month", tail=4,
                      window=10):
    
    #Es werden höchstens 3200 Tage gebraucht. Kürzung des Datensets, um Rechen
    #zeit zu reduzieren
    x = x[-3200:]    
        
    #Namen der Sektoren werden um 1 gekürzt, da in der ersten Spalte die Bench-
    #mark ist, die nicht abgebildet wird
    t_chart = t_chart[1:]
    
    #Umwandlung von String Format zu Datums Format
    dates = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates[-3200:]]
    
    #Unterteilung der Matrix in Benchmark (1. Spalte) und Sektoren (Rest)
    benchmark = np.array(x[:,0], dtype=float)
    assets = np.array(x[:,1:], dtype=float)
    
    
    
    ############################ Frequenz Anpassen ############################
    
    #Aus Tagereturns, Wochen- bzw. Monatsreturns machen. Kann unten in der
    #Funktion angepasst werden.
    if frequency == "week":
        asset_week = np.ones((1, assets.shape[1]))
        benchmark_week = np.array([])
        date_week = np.array([])
        for i in range(1, len(dates)):
            #Den letzten Tag der Woche finden.
            if dates[i-1].weekday() > dates[i].weekday():
                asset_week = np.concatenate((asset_week, assets[i-1].reshape(1,
                                             assets.shape[1])), axis=0)
                benchmark_week = np.append(benchmark_week, benchmark[i-1])
                date_week = np.append(date_week, np.array(dates[i-1], 
                                                          dtype=str))
        asset_week = np.concatenate((asset_week, assets[-1].reshape(1,
                                     assets.shape[1])), axis=0)
        benchmark_week = np.append(benchmark_week, benchmark[-1])
        date_week = np.append(date_week, np.array(dates[-1], dtype=str))        
        asset_week = asset_week[1:]
        assets = asset_week
        benchmark = benchmark_week
    elif frequency == "month":
        asset_month = np.ones((1, assets.shape[1]))
        benchmark_month = np.array([])
        date_month = np.array([])
        for i in range(1, len(dates)):
            if dates[i-1].month != dates[i].month:
                asset_month = np.concatenate((asset_month, assets[i-1].
                                        reshape(1,assets.shape[1])), axis=0)
                benchmark_month = np.append(benchmark_month, benchmark[i-1])
                date_month = np.append(date_month, np.array(dates[i-1], 
                                                            dtype=str))
        asset_month = np.concatenate((asset_month, assets[-1].reshape(1,
                                      assets.shape[1])), axis=0)
        benchmark_month = np.append(benchmark_month, benchmark[-1])
        date_month = np.append(date_month, np.array(dates[-1], dtype=str))        
        asset_month = asset_month[1:]
        assets = asset_month
        benchmark = benchmark_month  
    
    
    ############################## JdK RS-Ratio ###############################
    
    r_asset = (np.log(assets[1:]) - np.log(assets[:-1]))
    r_benchmark = (np.log(benchmark[1:]) - np.log(benchmark[:-1]))
    rs = 100 + (r_asset - r_benchmark.reshape(r_benchmark.shape[0],1)) * 100
    
    #Moving Average of the asset-benchmark ratio
    rs_ratio = np.ones((1,rs.shape[1]))

    for i in range(window, rs.shape[0]):
        rsr = np.nanmean(rs[i-window:i], axis=0)
        rs_ratio = np.concatenate((rs_ratio, rsr.reshape(1, rs.shape[1])), 
                                  axis=0)
    rs_ratio = rs_ratio[1:]    
    
    
    
    ############################# JdK RS-Momentum #############################

    rs_momentum = 100 * rs_ratio[1:]/rs_ratio[:-1]
    rs_ratio = rs_ratio[1:]
    
    ################################# Charts ##################################
    
    #Definierung einer PDF Datei, dorin alle Abbildungen gespeichert werden.
    pp = PdfPages(str(datei_name)+'.pdf')
    
    #Bestimmen wie viele Charts es geben wird.
    if assets.shape[1] % 5 == 0:
        N = int(assets.shape[1] / 5)
    else:
        N = int(assets.shape[1] / 5) + 1
    n = 1
    
    
    #Jeder RRG soll nur 5 Sektoren abbilden, da es sonst zu viel wird.
    for runde in range(0,assets.shape[1], 5):    
        x_max = np.nanmax( np.absolute(rs_ratio[-tail:, runde:runde+5] - 100))
        y_max = np.nanmax( np.absolute(rs_momentum[-tail:,
                                                   runde:runde+5] - 100))
        
        fig, ax = plt.subplots()
        plt.title("Relative Rotation Graph [" + str(n) + "/" + str(N) + "]", 
                                            fontsize=12, fontweight="bold")
        n += 1
        ax.set_yticks([100], minor=True)
        ax.yaxis.grid(True, which='major')
        ax.set_xticks([100], minor=True)
        ax.xaxis.grid(True, which='major')
        
        
        #Die 4 Quadranten bestimmen und färben
        
        #Finde die Maxima, um die Höhe und Breite des Charts und somit der 
        #Quadranten zu bestimmen.
        plt.xlim(100-x_max*1.1, 100+x_max*1.1)
        plt.ylim(100-y_max*1.1, 100+y_max*1.1)
        
        #Quadranten bestehen aus farbigen Rechtecken.
        rect = patches.Rectangle((100-x_max*1.1,100),x_max*1.1,y_max*1.1,
                                 linewidth=1, color='#D6FCFC')
        ax.add_patch(rect)
        rect = patches.Rectangle((100,100),x_max*1.1,y_max*1.1,linewidth=1, 
                                 color='#CFE8CF')
        ax.add_patch(rect)
        rect = patches.Rectangle((100-x_max*1.1,100-y_max*1.1),x_max*1.1,
                                 y_max*1.1,linewidth=1, color='#E7CFCF')
        ax.add_patch(rect)
        rect = patches.Rectangle((100,100-y_max*1.1),x_max*1.1,y_max*1.1,
                                 linewidth=1, color='#E8E8CF')
        ax.add_patch(rect)
        
        #Die einzelnen Sektoren werden einzeln geplottet und als "Kopf" wird
        #der letzte Punkt zusätzlich noch gescattert.
        for i in range(runde, runde+5):
            try:
                plt.plot(rs_ratio[-tail:, i], rs_momentum[-tail:,i], 
                         marker="s", markersize=4, label="Hallo")
                plt.scatter(rs_ratio[-1,i], rs_momentum[-1,i], linewidth=2.5, 
                            zorder=2)
                plt.annotate(t_chart[i],
                         (rs_ratio[-1,i],rs_momentum[-1,i]),
                         textcoords="offset points",
                         xytext=(0,4),
                         ha='center',
                         fontsize=5)
            except:
                break
        plt.xlabel("JdK RS-Ratio")
        plt.ylabel("JdK RS-Momentum")
        
        pp.savefig(bbox_inches='tight')
        
    return pp
            
            


            
###############################################################################
######################## Seasonality Charts + Heatmap #########################
############################################################################### 
def heat(x, dates, pp, t_chart, kistd=1.96):   
    
    #String Format in Datums Format umwandeln
    dates = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
    
    
    
    ################################# Heatmap #################################
    
    #Für jedes Datum die Monatsnummer (1 bis 12) erzeugen.
    month = [dates[i].month for i in range(len(dates))]
    
    #Tagesfrequenz in Monatsfrequenz umwandeln
    close = np.ones((1, x.shape[1]))
    close_dates = np.array([])
    for i in range(1, x.shape[0]):
        if month[i-1] != month[i]:
            close = np.concatenate((close, x[i].reshape(1, x.shape[1])),axis=0)
            close_dates = np.append(close_dates, month[i])        
    close = close[1:]
    month = close_dates
            
    

    #Matrizen definieren
    matrix_median = np.ones((close.shape[1],1))
    matrix_std = np.ones((close.shape[1],1))
    matrix_mean = np.ones((close.shape[1],1))
    
    #Für jeden Monat...
    for i in range(1,13):
        #...berechne den Monat zu Monat Return für, z.B., jeden Januar in den
        #letzten 10 Jahren
        rm = np.ones((1, close.shape[1]))
        for j in range(1, close.shape[0]):
            if i == month[j]:
                r = close[j]/close[j-1] - 1
                r = r.reshape(1, r.shape[0])
                rm = np.concatenate((rm, r), axis=0)
        rm = rm[1:,:]
        
        #Median, Standardabweichung, Durchschnitt bestimmen
        median = np.nanmedian(rm, axis=0)
        median = median.reshape(1, close.shape[1])
        matrix_median = np.concatenate((matrix_median, median.T), axis=1)
        std = np.nanstd(rm, axis=0)
        std = std.reshape(1, close.shape[1])
        matrix_std = np.concatenate((matrix_std, std.T), axis=1)
        mean = np.nanmean(rm, axis=0)
        mean = mean.reshape(1, close.shape[1])
        matrix_mean = np.concatenate((matrix_mean, mean.T), axis=1)
       
    #Erste Spalte löschen
    matrix_std = matrix_std[:,1:]    
    matrix_median = matrix_median[:,1:]


    #Daten ranken um eine Heatmap für jede Spalte zu erstellen
    matrix_rank = np.ones((close.shape[1],1))
    for i in range(12):
        rank = rankdata(matrix_median[:,i]).reshape(matrix_median.shape[0],1)
        matrix_rank = np.concatenate((matrix_rank, rank), axis=1)   
    matrix_rank = matrix_rank[:,1:]
    matrix_median = np.round(matrix_median*100, 1)
     
    
    
    #Heatmap erstellen
    beschriftung = np.array(["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", 
                             "Aug", "Sep", "Okt", "Nov", "Dez"])
    
    #Wenn 35 Sektoren, auf 5 Heatmaps aufteilen. Sieht besser aus    
    if matrix_rank.shape[0] == 35:
        N = 5
        n = 1
        for i in range(7, matrix_rank.shape[0]+7, 7):
            plt.figure()
            ax = sns.heatmap(matrix_rank[i-7:i], vmin = 1, vmax=close.shape[1],
                        cmap="YlGnBu", annot=matrix_median[i-7:i], cbar=False)
            bottom, top = ax.get_ylim()
            ax.set_ylim(bottom + 0.5, top - 0.5)
            ax.set_xticklabels(beschriftung)
            ax.set_yticklabels(t_chart[i-7:])
            ax.set_title( "Durchschnittliche Monatsrendite (in %) [" + str(n) +
                         "/" + str(N) + "]", fontsize=12, fontweight="bold")
            n += 1
            plt.yticks(rotation=0)
            pp.savefig(bbox_inches='tight')
            plt.show()             
    
    #Sonst, jeweils 10 pro Heatmap
    else:
        if matrix_rank.shape[0] % 10 == 0:
            N = int(matrix_rank.shape[0] / 10)
        else:
            N = int(matrix_rank.shape[0] / 10) + 1
        n = 1
        for i in range(10, matrix_rank.shape[0]+10, 10):
            plt.figure()
            ax = sns.heatmap(matrix_rank[i-10:i], vmin=1, vmax=close.shape[1],
                        cmap="YlGnBu", annot=matrix_median[i-10:i], cbar=False)
            bottom, top = ax.get_ylim()
            ax.set_ylim(bottom + 0.5, top - 0.5)
            ax.set_xticklabels(beschriftung)
            ax.set_yticklabels(t_chart[i-10:])
            ax.set_title( "Durchschnittliche Monatsrendite (in %) [" + str(n) +
                         "/" + str(N) + "]", fontsize=12, fontweight="bold")
            n += 1
            plt.yticks(rotation=0)
            pp.savefig(bbox_inches='tight')
            plt.show()


    
    ########################### Seasonality Charts ############################

    #Für jedes Datum die Wochennummer erzeugen.
    week = [dates[i].isocalendar()[1] for i in range(len(dates))]
    
    #Tagesfrequenz in Wochenfrequenz ändern.
    close = np.ones((1, x.shape[1]))
    close_dates = np.array([])
    for i in range(1, x.shape[0]):
        if week[i-1] != week[i]:
            close = np.concatenate((close, x[i].reshape(1, x.shape[1])),axis=0)
            close_dates = np.append(close_dates, week[i])
    close = close[1:]        
    week = close_dates        
    
    
      
    #Matrizen definieren
    matrix_median = np.ones((close.shape[1],1))
    matrix_std = np.ones((close.shape[1],1))
    matrix_mean = np.ones((close.shape[1],1))
    
    #Für jeden Monat...
    for i in range(1,53):
        #...berechne den Monat zu Monat Return für, z.B., jeden Januar in den
        #letzten 10 Jahren
        rm = np.ones((1, close.shape[1]))
        for j in range(1, close.shape[0]):
            if i == week[j]:
                r = close[j]/close[j-1] - 1
                r = r.reshape(1, r.shape[0])
                rm = np.concatenate((rm, r), axis=0)
        rm = rm[1:,:]
        
        #Median, Standardabweichung, Durchschnitt bestimmen
        median = np.nanmedian(rm, axis=0)
        median = median.reshape(1, close.shape[1])
        matrix_median = np.concatenate((matrix_median, median.T), axis=1)
        std = np.nanstd(rm, axis=0)
        std = std.reshape(1, close.shape[1])
        matrix_std = np.concatenate((matrix_std, std.T), axis=1)
        mean = np.nanmean(rm, axis=0)
        mean = mean.reshape(1, close.shape[1])
        matrix_mean = np.concatenate((matrix_mean, mean.T), axis=1)
     
    #Erste Spalte löschen
    matrix_std = matrix_std[:,1:]    
    matrix_median = matrix_median[:,1:]
    matrix_mean = matrix_mean[:,1:]



    #Geometrische Verkettung der durchschnittlichen Monatlichen Renditen,
    #um einen durchschnittlichen Jahresverlauf für jedes Asset zu erhalten.
    g_median = np.ones((matrix_median.shape[0],1))
    g_mean = np.ones((matrix_median.shape[0],1))
    for i in range(52):
        median = (1+matrix_median[:,i]).reshape(matrix_median.shape[0], 1)
        median_last = g_median[:,-1].reshape(matrix_median.shape[0], 1)
        g_median = np.concatenate((g_median, median_last*median), axis=1)
        mean = (1+matrix_mean[:,i]).reshape(matrix_mean.shape[0], 1)
        mean_last = g_mean[:,-1].reshape(matrix_mean.shape[0], 1)
        g_mean = np.concatenate((g_mean, mean_last*mean), axis=1)
    g_median = g_median[:,1:]   
    g_mean = g_mean[:,1:]    
    
        
    
    #Seasonality Charts erstellen
    for i in range(close.shape[1]):
        plt.title("Seasonal Chart: " + str(t_chart[i]), fontsize=12, 
                  fontweight="bold")
        plt.ylabel("Return in %")
        plt.xticks([4, 8, 12, 17, 21, 25, 30, 34, 38, 43, 47, 51], ["Jan",
                   "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug","Sep",
                   "Okt", "Nov", "Dez"])
        plt.plot(g_median[i], color="red")
        plt.plot(g_mean[i], color="green")
        plt.plot(g_mean[i]+kistd*matrix_std[i], color="blue", linewidth=0.1)
        plt.plot(g_mean[i]-kistd*matrix_std[i], color="blue", linewidth=0.1)
        plt.legend(["Median", "Mean", "Confidence Bands"], loc=2, 
                   fontsize="xx-small")
        pp.savefig(bbox_inches='tight')
        plt.show()
    
    #PDF Datei muss am ende geschlossen werden!!!
    pp.close()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

if __name__ == '__main__':
    import Data_Update_Sector
    
    #Namen der Dateien, die gelesen werden sollen
    name = ["MSCI_EMU_D", "MSCI_Europe_D", "MSCI_World_D", "ICB_Europe_D", 
            "ICB_NA_D", "ICB_World_D", "MSCI_Country_D", 
            "MSCI_Styles_Europe_D", "MSCI_Styles_USA_D", "MSCI_Styles_World_D"]	
    														
    for datei_name in name:
        
        #Beschriftung Dateiabhängig anpassen.
        if "ICB" in datei_name:
            #Namen der ICB Sektoren
            t_chart = [str(datei_name[:-2]), 'Oil&Gas', 'Chemicals', 
             'Basic Resources',	'Cnstrctn&Materials', 'Indu Goods&SVS',	
             'Auto&Parts', 'Food&Bvg', 'Prsnl&HH Goods', 'Health Care', 
             'Retail', 'Media', 'Travel&Leisure', 'Telecom', 'Utilities', 
             'Banks', 'Insurance', 'Real Estate', 'Fin SVS', 'Technology']
        elif "Country" in datei_name:
            t_chart = ['MSCI World', 'USA', 'Europe', 'Japan', 'Germany', 
             'Frankreich', 'UK', 'Switzerland', 'Spain', 'Italy', 'China']
        elif "Styles" in datei_name:
            t_chart = [str(datei_name[12:-2]), 'Value', 'Growth', 'Quality', 
             'Low Vola', 'High Yield', 'Momentum', 'Largecap', 'Smallcap']
        else:
            #Namen der MSCI Sektoren
            t_chart = [str(datei_name[:-2]), 'Energy',	'Materials',	
              'Chemicals', 'Basic Ress', 'Mining', 'Industrials', 
              'Capital Goods', 'Comm&Prof SVS',	'Transportation', 'Cons Disc', 
              'Auto&Comp', 'Cons Dur&App', 'Cons SVS', 'Retailing',	 
              'Consumer Staples', 'Food&Stpls', 'Food,Bvg&Tobacco', 
              'Household&PP', 'Health Care',	 'Pharma,Bio&Life', 'HC Equpm&SVS', 
              'Financials', 'Banks','Insurance',  'Div Fin', 'IT', 
              'Software&SVS', 'Hardware&SVS', 'Semicond&Equpm', 
              'Communication',	'Telecom SVS', 'Media', 'Utilities', 
              'Real Estate']
            
        #Die oben definierten Funktionen in Reihe geschaltet.
        x = pd.read_csv(datei_name + ".csv", delimiter=",")
        x, dates = miningreuters(x)
        pp = relative_rotation(x, dates, datei_name, t_chart,frequency="weeks", 
                               tail=4, window=12)   
        rs(x, dates, pp, t_chart)    
        heat(x, dates, pp, t_chart, kistd=1.96)
