import pandas as pd
import numpy as np
import xlwings as xw


###############################################################################
############################## Update-Protokoll ###############################
###############################################################################

#Update (31.03.2020): #Notwendigkeit von numberConst als Inputfaktor behoben im
#Teil "Constituents".

#Update (29.03.2020): Länge von matrix_cons und matrix_daten anpassen, wenn 
#diese unterschiedlich lang sein sollten. Ist trotzdem noch als !!! markiert. 
#Bitte überprüfen.

###############################################################################
###############################################################################
###############################################################################



def mining(constFileName, chgFileName, dataFileName, indexTicker):
    
    
    ###########################################################################
    ############################## Constituents ###############################
    ###########################################################################
    
    #2 Spalten: 0 Spalte=Datum, 1 Spalte=String mit allen Constituents, die zu 
    #dem Zeitpunkt gab
    cons = pd.read_csv(str(constFileName) + ".csv") 
    
    #Datum wird als Index gemacht
    cons1 = pd.DataFrame(cons.values[:,1:], 
                    index=pd.to_datetime(cons.values[:,0], format="%Y-%m-%d")) 
    
    
    
    #Numpy Array mit den reinen Strings, die im folgenden auseinander 
    #gefriemelt werden
    cons = np.array(cons1.values, dtype=str)    
    liste_cons = []
    
    for i in cons:
        #Trennt die Strings nach jedem Komma
        cons_v = np.array(str(i).split(","), dtype=str)
        
        #Löscht alle Char Kombinationen die unten im Array stehen
        for c in ["[", "]", "'", '"', " "]:
            cons_v = np.char.replace(cons_v, c, "")
        
        liste_cons.append(cons_v)
    
    
    #Liste -> DataFrame
    df = pd.DataFrame(liste_cons)
    
    #Die Leeren Zellen werden im DataFrame als "None" deklariert. Ich möchte
    #aber komplett leere Zellen haben und ersetze diese mit "".
    df = np.array(df.values, dtype=str)
    df = np.char.replace(df, "None", "")
    
    #Finales DataFrame
    matrix_cons = pd.DataFrame(df, index=cons1.index)
    
        
    
    
    
    ###########################################################################
    ################################### CHG ###################################
    ###########################################################################
    
    #Matrix mit den Joinern und Leavern
    chg = pd.read_csv(str(chgFileName) + ".csv")
    matrix_chg = pd.DataFrame(chg.values[:,3:], columns=["Ereignis", "Asset"], 
        index=pd.to_datetime(chg.values[:,2], format="%Y-%m-%d")).sort_index()
    
    
    
    
    
    ###########################################################################
    ################################## Data ###################################
    ###########################################################################
    
    #Matrix mit den Preisen
    #Columns: Unnamed: 0, Instrument, Date, Total Return
    data = pd.read_csv(str(dataFileName) + ".csv") 
    
    #Index: Date; Columns: Instrument, Total Return
    data = pd.DataFrame(np.delete(data.values[:,1:], 1,1), 
        index=pd.to_datetime(data.values[:,2], format="%Y-%m-%d")) 
    
    
    
    #Liste mit den Instruments, damit man später den Schnitt dort machen kann,
    #wenn sich das Instrument ändert.
    asset_list = np.array(data.values[:,0], dtype=str)
    
    datum = list(data.index)
    preise = np.array(data.values[:,1], dtype=float)
    daten = []
    
    #Brauche einen Startwert, weil DFs kacke sind und nur Bereiche ansprechen 
    #können...
    start = 0
    
    for i in range(1,asset_list.shape[0]):
        #Trennt die Zeitreihen, wenn sich die Asset Bezeichnung ändert
        if asset_list[i] != asset_list[i-1]:
            df = pd.DataFrame(preise[start:i]/100, index=datum[start:i], 
                              columns=[asset_list[i-1]]).dropna()
            start = i
            daten.append(df)
        
        #Wenn Asset Bezeichnung gleich bleibt, werden die Preise unter das 
        #derzeitige Array gepackt
        if i == asset_list.shape[0]-1:
            df = pd.DataFrame(preise[start:]/100, index=datum[start:], 
                              columns=[asset_list[i-1]]).dropna()
            daten.append(df)
    
    
    
    #Bestimmt die Zeitreihe mit der längsten Zeilenanzahl und nimmt deren 
    #Datum als das Datum, was später für die matrix_daten benutzt wird.        
    max_len = 0
    for i in range(len(daten)):
        if len(daten[i]) > max_len:
            max_len = len(daten[i])
            j = i 
    
    langste_datum = list(daten[j].index)
    
    
    
    #Umbau des Datum in der Index Spalte, da es vorkommt, dass bei einigen 
    #Assets der Schlusskurs vom Datum her z.B. der Donnerstag ist und beim Rest 
    #der Freitag. Das Resultat ist, dass in vielen Zeilen in der finalen Matrix 
    #nur ein Eintrag stehen würde. Daher wird statt dem Datum ein neuer Index 
    #erstellt, der aus dem Jahr und der Wochennummer besteht.
    for i in range(len(daten)):
        asset_daten = daten[i].index
        asset_year = list(asset_daten.year)
        asset_week = list(asset_daten.week)
        asset_index_new = np.array([])
        
        for year, week in zip(asset_year, asset_week):
            #Wenn die 0 nicht hinzugefügt werden würde, wären die Indizes nicht 
            #gleich lang und ließen sich nicht sortieren. Der Index muss eine 
            #Zahl sein, die stetig größer wird!
            if week < 10:
                week = "0" + str(week)
            asset_index_new = np.append(asset_index_new, int(str(year) + 
                                                             str(week)))
        
        daten[i] = pd.DataFrame(daten[i].values, index=asset_index_new, 
                 columns=daten[i].columns)
            
    matrix_daten = daten[0]
    
    
    
    #Die Zeitreihen werden nebeneinander in eine Matrix gepackt. Der pd.concat 
    #Befehl sorgt dafür, dass das Datum übereinstimmt
    for d in daten[1:]:
        try:
            matrix_daten = pd.concat([matrix_daten, d], axis=1)
        except:
            #Gibt die Assets aus, die nicht in die Matrix passen, weil sie eine 
            #Länge von 0 haben.
            print(d.columns)
            print(len(d))
            print(len(d.columns))
            pass
    
    matrix_daten2 = matrix_daten.values
    
    
    
    
    ######## NEU ######!!!
    #Ausreisser ersetzen
    for i in range(matrix_daten.shape[1]):
        matrix_daten2[:,i] = np.where(matrix_daten.values[:,i] > 0.7, 
                                    np.nanmedian(matrix_daten.values[:,i]), matrix_daten.values[:,i])
        
    matrix_daten = pd.DataFrame(matrix_daten2, index=matrix_daten.index, 
                                 columns=matrix_daten.columns)
    
    #Zum Schluss wird der Index mit einer richtigen Datumsliste ersetzt        
    matrix_daten = pd.DataFrame(matrix_daten.values, index=langste_datum, 
                                columns=matrix_daten.columns)
    ###################
    
    
    #Einmal bitte auf Richtigkeit prüfen: Nach meinem Verständnis, wird
    #jeden Sonntag die Liste der aktuellen Constituents bekannt gegeben. Z.B.
    #am 01.01.. Die Dazugehörigen Wochenreturns wären dann am Freitag dieser
    #Woche, also dem 06.01.. In diesem Datenset werden aber Constituents von
    #einer Woche bekannt gegeben, wozu es noch keine Returns gibt (z.B. da 
    #Daten schon am Mittwoch abgerufen). Also cons >= returns, weshalb ich
    #einfach, wenn nötig, die letzten matrix_cons Einträge abschneide, damit
    #beide Matrizen die selbe Länge haben.
    matrix_cons = matrix_cons.iloc[:-(matrix_cons.shape[0]-
                                      matrix_daten.shape[0])]

    
    
    
    ###########################################################################
    ################################ Verfügbar ################################
    ###########################################################################
    
    #Als Index wird der Index von matrix_daten genommen, damit diese 
    #übereinstimmen. Das Datum der Constituents gibt immer den Montag einer 
    #Woche an und die Preise beziehen sich auf den Freitag.
    matrix_cons = pd.DataFrame(matrix_cons.values, columns=matrix_cons.columns, 
                               index=matrix_daten.index)
    
    
    
    #Erstelle eine Matrix die aus nan besteht, um sie später mit 1 aufzufüllen.
    matrix = np.full(matrix_daten.shape, np.nan)
    i = 0
    
    for p in matrix_daten.index:
        for j in range(len(matrix_daten.columns)):
            #Wenn ein Return verfügbar ist, und das Asset in bei den aktuellen 
            #Constituents gelistet ist, wird in diese Zelle eine 1 vergeben. 
            #Sonst bleibt sie nan. Annahme: Wir setzen unsere Orders Freitag
            #nach Börsenschluss. Schlusskurse für diese Woche sind bekannt. Wir
            #wissen aber nicht, ob nächste Woche das Asset noch im Index sein
            #wird. 
            if (        np.isnan(matrix_daten[p:p].loc[p].iloc[j]) == 0 
                and (matrix_daten.columns[j] in matrix_cons[p:p].values)
            ):
                matrix[i,j] = 1
            else:
                matrix[i,j] = np.nan
        i += 1
     
        
        
    matrix_verfugbar = pd.DataFrame(matrix, columns=matrix_daten.columns, 
                                    index=matrix_daten.index)
    
    
    
    
    
    ###########################################################################
    ######################## Als xlsx Datei speichern #########################
    ###########################################################################
    
    wb = xw.Book()
    ws = wb.sheets.add("Verfügbar")
    ws.range("A1").value = matrix_verfugbar   
    ws = wb.sheets.add("Preise")
    ws.range("A1").value = matrix_daten
    ws = wb.sheets.add("CHG")
    ws.range("A1").value = matrix_chg
    ws = wb.sheets.add("Constituents")
    ws.range("A1").value = matrix_cons
    wb.sheets("Tabelle1").delete()
    wb.save("data_set_" + str(indexTicker) + ".xlsx")








  
if __name__ == '__main__':
    idx = "DJI"
    constFileName = str(idx) + "_cons"
    chgFileName= str(idx) + "_consCHG"
    dataFileName= str(idx) + "_data"
    indexTicker= str(idx)
    
    mining(constFileName, chgFileName, dataFileName, indexTicker)
