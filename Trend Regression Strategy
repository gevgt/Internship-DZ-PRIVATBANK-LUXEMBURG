import pandas as pd
import numpy as np
from scipy.stats import rankdata
import back_testing as bt





#Programmeinstellungen
################################
pf_size = 15
pct_first_round = 0.5
index_size = 30
################################




x = pd.read_excel("data_set_DJI.xlsx", sheet_name=["Constituents", "CHG", 
                                        "Preise", "Verfügbar"], index_col=0)


constituents = x["Constituents"]
chg = x["CHG"]
preise = x["Preise"]
verfugbar = x["Verfügbar"]




#Kontrolliert für Fehler
for i in range(preise.shape[0]):
    for j in range(preise.shape[1]):
        if (
                np.isnan(preise.values[i,j])==1   and 
                np.isnan(preise.values[i-1,j])==0 and 
                np.isnan(preise.values[i+1,j])==0
            ):
            print(i,j)

 
    

#Definiert zwei Matrizen die nan enthalten
trend = np.full(preise.shape, np.nan)
std = np.full(preise.shape, np.nan)


#Erklärende Variable: bleibt immer gleich. Geht von 0 bis 51
x_v = np.concatenate((np.ones((52,1)), np.arange(52).reshape(52,1)), axis=1)


#Regression und Standardabweichung der Fehlerterme
#Starte 52 Wochen später, da ich 1 Jahr für die Trendschätzung brauche
for i in range(52, preise.shape[0]):
    for j in range(preise.shape[1]):     
        
        #Erklärte Variable: Vor 52 Wochen bis letzte Woche. Aktuellen Return 
        #lasse ich weg
        y_v1 = np.array(preise.iloc[i-52:i,j].values, dtype=float)
        
        #Geometrisch verknüpfen, damit die Trendlinie durch einen Verlauf 
        #gelegt werden kann und nicht einfach nur durch returns.
        y_v = np.array([1])
        for k in range(52):
            y_v = np.append(y_v, y_v[-1]*(1+y_v1[k]))
        
        y_v = y_v[1:].reshape(52,1)
        
        
        #Betas
        beta = np.matmul( np.linalg.inv(np.matmul(x_v.T, x_v)), 
                         np.matmul(x_v.T, y_v))
        
        #Std der Residuen
        e = np.std(np.matmul(x_v,beta) - y_v)
        
        #Trage die Ergebnisse in die heutige Zelle für jedes Asset ein
        std[i,j] = e
        trend[i,j] = beta[1]
   

#Multipliziere std und trend mit der Matrix verfügbar, um alle Assets zu 
#löschen, die nicht Verfügbar sind zu dem Zeitpunkt
trend = pd.DataFrame(trend * verfugbar, index=preise.index, 
                     columns=preise.columns)
std = pd.DataFrame(std * verfugbar, index=preise.index, columns=preise.columns)


rank_trend = np.full((52,trend.shape[1]), np.nan)
for i in range(52, trend.shape[0]):
    #Ranken der Trends
    #Der Beste ist die Nr. 53
    rank_trend = np.concatenate((rank_trend, 
                rankdata(np.where(np.isnan(trend.values[i])==1, -1000, 
                trend.values[i]), method='ordinal').reshape(1,trend.shape[1])),
                axis=0)

       
#Multiplizieren mit verfugbar, um die nicht investierbaren Assets zu löschen    
rank_trend = pd.DataFrame(rank_trend * verfugbar, index=preise.index, 
                          columns=preise.columns)




#Step 1: Sucht die besten 50% gemessen an der Steigung von den 30 Titeln raus, 
#die im Moment verfügbar sind
#Der Rest, der die Bedingung nicht erfüllt wird nan
matrix_trend = np.where(rank_trend > trend.shape[1]-index_size*pct_first_round,
                        1, np.nan)




#Step 2: Sucht die Top 10 raus um daraus ein Portfolio zu machen
#Mit matrix_trend mulitplizieren um alle Assets zu löschen, die in Step 1 
#rausgeflogen sind
std2 = std * matrix_trend

rank_std = np.full((52,trend.shape[1]), np.nan)
for i in range(52, trend.shape[0]):
    #Der Beste ist die Nr. 1     
    rank_std = np.concatenate((rank_std, 
                rankdata(np.where(np.isnan(std2.values[i])==1, 1000, 
                std2.values[i]), method='ordinal').reshape(1,trend.shape[1])), 
                axis=0)
    
rank_std = pd.DataFrame(rank_std * matrix_trend, index=preise.index, 
                        columns=preise.columns)
rank_std = np.where(rank_std <= pf_size, 1, np.nan) #10




#Relevante Returns finden
returns = rank_std * preise
num_assets = np.sum(np.where(np.isnan(returns)==0, 1, 0), axis=1)
returns = (np.nanmean(rank_std * preise, axis=1) + 1)[51:]




#Geometrisch verknüpfen
pf = np.array([1])
for i in range(1, returns.shape[0]):
    pf = np.append(pf, pf[-1]*returns[i])   
pf = pd.DataFrame(pf, index=preise.index[51:]).iloc[:-1]




#Benchmark erstellen
z = pd.read_csv("^DJI.csv", index_col=0)
z = pd.DataFrame(z.values[:,3], index=pd.to_datetime(z.index, 
                 format="%Y-%m-%d")).iloc[1:]

r2 = preise * verfugbar
r2 = pd.DataFrame(np.nanmean(r2, axis=1), index=r2.index)

r2_a = np.array([1])
for i in range(1,r2.shape[0]):
    r2_a = np.append(r2_a, r2_a[-1]*(1+r2.values[i]))
    
r2_a = pd.DataFrame(r2_a[51:]/r2_a[51], index=r2.index[51:])




#Auswertung der Zeitreihen
knz = bt.kennzahlen(x, pf, start="2002-02-14", bm=z)  
