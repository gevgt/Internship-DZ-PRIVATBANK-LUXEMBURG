import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import rankdata
import back_testing as bt


#Gibt an, wie viele Titel im Portfolio sein sollen
pf = 15


#Lädt das gewünschte Datenset, welches mit "Mining" erstellt wurde.
x = pd.read_excel("data_set_DJI.xlsx", sheet_name=["Constituents", "CHG", 
                                        "Preise", "Verfügbar"], index_col=0)


#Benennt die Variablen, damit man nicht mit einer Liste von Matrizen arbeiten
#muss
constituents = x["Constituents"]
chg = x["CHG"]
preise = x["Preise"] #sind returns
verfugbar = x["Verfügbar"]




#Definiert Variablen
preise_ts = np.ones((1, preise.shape[1]))


#Wenn keine Returns Verfügbar wird, wird der Return auf 0 gesetzt, ansonsten
#wird der ursprüngliche Preis beibehalten
preise2 = np.where(np.isnan(preise)==1, 0, preise)


#Eine Returns werden geometrisch Verknüpft
for i in range(preise2.shape[0]):
    vektor = preise_ts[-1] * (1+preise2[i])
    preise_ts = np.concatenate((preise_ts, 
                                vektor.reshape(1, preise2.shape[1])), axis=0)




#Die Momentum Variable wird erstellt. Die 51 steht für die letzten 52 Wochen
#(1 Jahr) ohne die letzte Woche
momentum = preise_ts[51:] / preise_ts[:-51] -1
momentum = momentum[:-1]

#Die Matrix mit den Momentum Werten wird mit der Verfügbarkeitsmatrix, welche
#aus 1 und 0 besteht multipliziert, um nur noch die Werte übrig zu haben, die
#man zu dem Zeitpunkt auch benutzen darf.
momentum = momentum * verfugbar.values[51:]
momentum_df = pd.DataFrame(momentum, index=preise.index[-momentum.shape[0]:], 
                           columns=preise.columns)


#Es wird eine Matrix erstellt mit dem jeweiligen Rang des Assets zum jeweiligen
#Zeitpunkt
rank = np.ones((1,momentum.shape[1]))
for i in range(momentum.shape[0]):
    #Bevor die Momentum werte geranked werden, werden alle nicht verfügbaren
    #Werte durch 1000 ersetzt. Ansonsten -Momentum, damit der beste Wert
    #(kleinstes -Momentum) den Platz 1 erhält.
    rank = np.concatenate((rank, rankdata(np.where(np.isnan(momentum[i])==1, 
        1000, -momentum[i]), method='ordinal').reshape(1,momentum.shape[1])), 
        axis=0)


#Alle Ränge die kleiner gleich der Gewünschten Portfoliogröße sind, bekommen
#eine 1, sonst nan.    
rank = np.where(rank <= pf, 1, np.nan)[1:]
rank_df = pd.DataFrame(rank, index=momentum_df.index, 
                       columns=momentum_df.columns)


#Die Matrix preise2 wird gekürzt, sodass sie die gleiche Länge hat wie die 
#momentum Matrix
preise2 = preise2[-momentum.shape[0]:]


#Es bleiben nur die Returns stehen, die es in das Portfolio geschafft haben,
#der Rest bekommt eine 0
portfolio = preise2[1:] * rank[:-1]
portfolio_df = pd.DataFrame(portfolio, index=rank_df.index[1:], 
                            columns=rank_df.columns)


#Nun wird der Durschnitt über alle Spalten genommen. Da np.nanmean genutzt
#wird, werden nur die Werte berücksichtigt, die nicht nan sind.
pfReturns = np.nanmean(portfolio, axis=1)


#Die Returns des Portfolios werden geometrisch verknüpft
pfZeitReihe = np.array([1])
for i in range(pfReturns.shape[0]):
    pfZeitReihe = np.append(pfZeitReihe, pfZeitReihe[-1] * (1+pfReturns[i]))    
pfZeitReihe = pd.DataFrame(pfZeitReihe, 
                           index=preise.index[-pfZeitReihe.shape[0]:])




#Die Benchmark wird erstellt
bm = np.nanmean(preise * verfugbar, axis=1)
bm1 = np.array([1])
for i in range(bm.shape[0]):
    bm1 = np.append(bm1, (1+bm[i])*bm1[-1])    
bm = pd.DataFrame(bm1[-pfZeitReihe.shape[0]:], index=pfZeitReihe.index)




#Auswertung der Zeitreihe mit Hilfe der "Back Testing Environment"
knz = bt.kennzahlen(x, pf=pfZeitReihe, start="1995-12-29", bm=bm)
