import pandas as pd
import numpy as np


# AD-Line: Advances & Declines
def adLine(index,window):
    
    for i in range(index.shape[0]):
        advance = np.sum(np.where(index.values[i] > 0, 1, 0))
        decline = np.sum(np.where(index.values[i] < 0, 1, 0))
        netAdvances = advance - decline
        
        if i == 0:
            adLine = np.array([netAdvances])
            ad = np.array([advance])
            de = np.array([decline])
        else:    
            adLine = np.append(adLine, adLine[-1] + netAdvances)
            ad = np.append(ad,advance)
            de = np.append(de,decline)
            
    adLine = pd.DataFrame(adLine, index=index.index, columns = ["AD Line"])    
    ad = pd.DataFrame(ad, index=index.index, columns = ["Advances"])    
    de = pd.DataFrame(de, index=index.index, columns = ["Declines"])    
    
    # Moving Average der Advances und Declines
    for j in [ad,de]:
        for i in window:
            g = j.columns[0] + " "+ str(i) +"W" 
            j[g] = j.iloc[:,0].rolling(window=i).mean()
    
    ad_de = pd.concat([ad,de],axis=1)
    return adLine, ad_de




# Net New Highs
def netNewHighs(returns, verfugbar, window):
    
    # Return-Vorbereitung
    returns_ts = np.ones((1, returns.shape[1]))
    returns2 = np.where(np.isnan(returns)==1, 0, returns)
    
    # Kumulierte Returns
    for i in range(returns2.shape[0]):
        vektor = returns_ts[-1] * (1+returns2[i])
        returns_ts = np.concatenate((returns_ts, 
                                vektor.reshape(1, returns2.shape[1])), axis=0)
    returns_ts = returns_ts[1:] * verfugbar

    
    highLowline_tot = pd.DataFrame(index=returns.index)
    netNewHighs_tot = pd.DataFrame(index=returns.index)
    
    for j in window:
        netNewHighs = np.array([])
        high_tot = np.array([])
        low_tot = np.array([])

        for i in range(j, returns_ts.shape[0]):
            high = np.sum(np.where(returns_ts.values[i] > 
                                   np.nanmax(returns_ts[i-j:i], axis=0), 1, 0))
            low = np.sum(np.where(returns_ts.values[i] < 
                                  np.nanmin(returns_ts[i-j:i], axis=0), 1, 0))
            net = high - low
        
            netNewHighs = np.append(netNewHighs, net)
            high_tot = np.append(high_tot, high)
            low_tot = np.append(low_tot, low)

            if i == j:
                highLowLine = np.array([net])
            else:    
                highLowLine = np.append(highLowLine, highLowLine[-1] + net)
    
        highLowLine = pd.DataFrame(highLowLine, index=returns.index[j:], 
                                   columns=["High Low Line "+ str(j) +"w"])        
        netNewHighs = pd.DataFrame(netNewHighs, index=returns.index[j:], 
                                   columns=["Net New Highs "+ str(j) +"w"])
        
        highLowline_tot = pd.concat([highLowline_tot,highLowLine],axis=1)
        netNewHighs_tot = pd.concat([netNewHighs_tot,netNewHighs],axis=1)
        
    return netNewHighs, highLowLine, high_tot, low_tot




#Percent above Moving Average
def pAboveMa(returns, verfugbar, window):


    returns_ts = np.ones((1, returns.shape[1]))
    returns2 = np.where(np.isnan(returns)==1, 0, returns)
    
    # Kumulierte Performance
    for i in range(returns2.shape[0]):
        vektor = returns_ts[-1] * (1+returns2[i])
        returns_ts = np.concatenate((returns_ts, 
                                vektor.reshape(1, returns2.shape[1])), axis=0)
    
    pAboveMa_tot = pd.DataFrame(index=returns.index)
    
    for w in window:
        ma = pd.DataFrame(returns_ts[1:], index=returns.index,
                         columns=returns.columns).rolling(w).mean() * verfugbar
    
        pAboveMa = pd.DataFrame(np.nansum(np.where(ma < 
                    returns_ts[1:]*verfugbar, 1, 0), axis=1) / 
                    np.nansum(np.where(np.isnan(ma) == 0, 1, 0), axis=1), 
                    index=returns.index, 
                    columns=["Percentage above MA "+str(w)+"w"])
        pAboveMa_tot = pd.concat([pAboveMa_tot,pAboveMa],axis=1)
        
    return pAboveMa_tot
