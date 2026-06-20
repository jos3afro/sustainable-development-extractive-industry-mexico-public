# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 11:51:42 2023
Sample code 
@author: Jos3
"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from config import ROOT, CENSO1990, CENSO2000, CENSO2010, CENSO2020, CORE, NDVI_DIR, LANDUSE, RESULTS




import pandas as pd
import numpy as np
from simpledbf import Dbf5

def dummies( origin, var, yes):
    if type(yes)==list:
        origin.loc[~origin[var].isin(yes), var]=0
        origin.loc[origin[var].isin(yes), var]=1
    else:
        origin.loc[~origin[var].isin([yes]), var]=0
        origin.loc[origin[var].isin([yes]), var]=1

    
def df_create(y):
    db=pd.DataFrame() 
    for x in y :
        temp = Dbf5(x)
        temp = temp.to_dataframe()
        db = pd.concat([db, temp], axis=0)
    for i in list(db.columns):
            try:
                db[i] = db[i].astype(int)
            except:
                pass
    return(db)
        #del temp 


paths = [str(CENSO1990 / 'm_1001.dbf'),
str(CENSO1990 / 'm_1002.dbf'),
str(CENSO1990 / 'm_1003.dbf'),
str(CENSO1990 / 'm_1004.dbf'),
str(CENSO1990 / 'm_1005.dbf'),
str(CENSO1990 / 'm_1006.dbf'),
str(CENSO1990 / 'm_1007.dbf'),
str(CENSO1990 / 'm_1008.dbf'),
str(CENSO1990 / 'm_1009.dbf'),
str(CENSO1990 / 'm_1010.dbf'),
str(CENSO1990 / 'm_1011.dbf'),
str(CENSO1990 / 'm_1012.dbf'),
str(CENSO1990 / 'm_1013.dbf'),
str(CENSO1990 / 'm_1014.dbf'),
str(CENSO1990 / 'm_1015.dbf'),
str(CENSO1990 / 'm_1016.dbf'),
str(CENSO1990 / 'm_1017.dbf'),
str(CENSO1990 / 'm_1018.dbf'),
str(CENSO1990 / 'm_1019.dbf'),
str(CENSO1990 / 'm_1020.dbf'),
str(CENSO1990 / 'm_1021.dbf'),
str(CENSO1990 / 'm_1022.dbf'),
str(CENSO1990 / 'm_1023.dbf'),
str(CENSO1990 / 'm_1024.dbf'),
str(CENSO1990 / 'm_1025.dbf'),
str(CENSO1990 / 'm_1026.dbf'),
str(CENSO1990 / 'm_1027.dbf'),
str(CENSO1990 / 'm_1028.dbf'),
str(CENSO1990 / 'm_1029.dbf'),
str(CENSO1990 / 'm_1030.dbf'),
str(CENSO1990 / 'm_1031.dbf'),
str(CENSO1990 / 'm_1032.dbf') ]





### Cleaning the data 
#print(df1990.columns)


df1990 = df_create( paths )

## Creating enrollment 

school1990 = df1990.loc[df1990['ANO_CUMP'].isin([  15, 16, 17]), 
            ['ENT', 'MUN', 'SEXO', 'ANO_CUMP', 'ASISTE','APROBO', 'PRESCO',
            'TEC_PRIM', 'TEC_SEC', 'NOR_BAS', 'NIV_EST', 'ANO_APRO']]

school1990.loc[school1990['ANO_APRO'].isin([999]), 'ANO_APRO']= np.nan 

school1990 = school1990.reset_index()
school1990.loc[school1990['NIV_EST'].isin([0] ), 'ESCOACUM']= 0
school1990.loc[school1990['NIV_EST'].isin([1] ), 'ESCOACUM'] = school1990['ANO_APRO']
school1990.loc[school1990['NIV_EST'].isin([2] ), 'ESCOACUM']= school1990['ANO_APRO']+6
school1990.loc[school1990['NIV_EST'].isin([3] ), 'ESCOACUM']= school1990['ANO_APRO']+9 
school1990.loc[school1990['NIV_EST'].isin([4] ), 'ESCOACUM']= school1990['ANO_APRO']+12
school1990.loc[school1990['NIV_EST'].isin([5] ), 'ESCOACUM']= school1990['ANO_APRO']+16

school1990 = school1990.groupby(['ENT', 'MUN']).agg({'ASISTE': lambda x: sum(x == 1), 'ANO_CUMP': 'count' , 
                                                     'ESCOACUM': 'mean'}).reset_index()

school1990.rename(columns={"ANO_CUMP": "COUNT_PPL"}, inplace=True)
school1990['ENROLL_RATE'] = school1990['ASISTE'] / school1990['COUNT_PPL']
municipalities = str(CENSO2020 / 'Municipalities info.csv')
mex_info= pd.read_csv(municipalities)

school1990 = school1990.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
school1990 = school1990[['ENT', 'MUN', 'CVEGEO','ASISTE', 'COUNT_PPL', 'ENROLL_RATE', 'ESCOACUM' ]]
school1990.to_csv(str(CENSO1990 / 'school90.csv'), index = True)
del school1990

##We need to create a viv index

df1990.loc[df1990.CVE_PAR.isin([ 100, 101, 102, 103, 105, 700, 701, 703, 708, 712, 716, 799 ]), 'Head_family'] = 1
df1990['Head_family'] = df1990.Head_family.fillna(0)
df1990['Family_N'] = df1990.groupby(df1990['FOLIO_VIV'])['Head_family'].cumsum()
df1990['ID_VIV'] = df1990.apply(lambda x: str(x['ENT']) + 'm' +str(x['MUN']) + 'v' + str(x['FOLIO_VIV']) + 'n' + str(x['Family_N']) , axis=1) 

## And Create a dummy if someone in the family works in mining
minin_codes = [1102 , 1202 , 5110 , 5111 , 5112 , 511 , 521 , 5210 , 5211 , 5212 , 5213 , 531 , 5310 , 5311 , 541 , 5410 , 5411 ]
df1990.loc[df1990.CVE_OCUP.isin(minin_codes), 'mining'] = 1
df1990['mining'] = df1990.mining.fillna(0)
## For ppl info (head mostly) 

## y=df1990.loc[df1990.ID_VIV == '2.0m1.0v137.0n1.0']	Tocheck households 
##algo=pd.DataFrame(data=df1990[['FOLIO_VIV', 'CVE_PAR', 'ID_VIV', 'Family_N' ,'SEXO' , 'ANO_CUMP', 'N_F_GPOS', 'NUM_PER', 'INGRESO']]) To check random shit behavior
## df['ENT'].value_counts() To see frequency of a column OR describe()


temp = df1990.groupby('ID_VIV')['INGRESO'].sum() #Note that im gonna drop those households without head of family
temp2 = df1990.groupby('ID_VIV')['mining'].max()

df1990 = df1990.loc[df1990['CVE_PAR'].isin([  100, 101, 102, 103, 105, 700, 701, 703, 708, 712, 716, 799]), 
            ['ENT', 'MUN', 'ID_VIV', 'SEXO', 'ANO_CUMP', 'HAB_IND', 'HORAS', 'NIV_EST', 'ANO_APRO', 'CVE_OCUP', 'SIT_TRAB', ##Until here are from ppl
                                                            'T_VIV', 'PAREDES', 'TECHOS', 'PISOS', 'P_DORMIR', 'T_CUARTOS', 'CUA_EXCLU', 'TAM_DUERME', 
                                                            'TIE_EXCU',  'CON_AGUA', 'AGUA_ENTU', 'DRENAJE', 'ELECTRI', 'COMBUS', 'TENENCIA',
                                                            'NUM_PERS', 'F_G_COC', 'N_F_GPOS', 'NUM_PER', 'TIP_HOGAR' ]]
for i in temp , temp2 :
    df1990 = pd.merge(df1990, i, on= 'ID_VIV' , how = 'inner' )

del temp , temp2

df1990.rename(columns={"CUA_EXCLU": "COCINA", 'TIE_EXCU' : 'SERSAN' , 'HAB_IND' : 'HLENGUA' , 'ANO_CUMP' : 'EDAD' , 'COMBUS' : 'COMBUST'}, inplace=True)
   
##For the household info    
  
dummies( df1990,  'PAREDES', 7)
dummies( df1990,  'TECHOS', [4, 5])
dummies( df1990,  'PISOS', [2, 3])
dummies( df1990,  'COCINA', 1)
dummies( df1990,  'SERSAN', 1) #Tiene sanitario
dummies( df1990,  'CON_AGUA', 3)
dummies( df1990,  'AGUA_ENTU', 1 )
dummies( df1990,  'DRENAJE', [1, 2] )
dummies( df1990,  'ELECTRI', 1 )
dummies( df1990,  'COMBUST', [3, 4] )

#Of the ppl
dummies( df1990,  'HLENGUA', 1 )


variable = ['TENENCIA', 'TIP_HOGAR' , 'SIT_TRAB' ] #to make dummies

for x in variable :
    data_dummies = pd.get_dummies(df1990[x],prefix=x)
    df1990 = pd.concat([df1990, data_dummies], axis=1)

to_delete = ['TENENCIA_9' , "TIP_HOGAR_7", "SIT_TRAB_9" ]
for i in to_delete:
        try:
            df1990.drop([i], axis=1, inplace=True)
        except:
            pass


df1990.loc[df1990['P_DORMIR'].isin([99]), 'P_DORMIR']= np.nan 
df1990.loc[df1990['T_CUARTOS'].isin([99]), 'T_CUARTOS']= np.nan 
df1990.loc[df1990['EDAD'].isin([999]), 'EDAD']= np.nan 
df1990.loc[df1990['ANO_APRO'].isin([999]), 'ANO_APRO']= np.nan 

##For years of schooling 
df1990.loc[df1990['NIV_EST'].isin([0] ), 'ESCOACUM']= 0
df1990.loc[df1990['NIV_EST'].isin([1] ), 'ESCOACUM']= df1990['ANO_APRO']
df1990.loc[df1990['NIV_EST'].isin([2] ), 'ESCOACUM']= df1990['ANO_APRO']+6
df1990.loc[df1990['NIV_EST'].isin([3] ), 'ESCOACUM']= df1990['ANO_APRO']+9 
df1990.loc[df1990['NIV_EST'].isin([4] ), 'ESCOACUM']= df1990['ANO_APRO']+12
df1990.loc[df1990['NIV_EST'].isin([5] ), 'ESCOACUM']= df1990['ANO_APRO']+16
    
df1990['year']= 1990

##Adding CVEGEO
municipalities = str(CENSO2020 / 'Municipalities info.csv')
mex_info= pd.read_csv(municipalities)

df1990 = df1990.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')

df1990.to_csv(str(CENSO1990 / 'data_mexico90.csv'), index = True)

del i, data_dummies, df1990, minin_codes, to_delete, variable, x


paths = [str(CENSO2000 / 'VHO_F01.DBF'),
str(CENSO2000 / 'VHO_F02.DBF'),
str(CENSO2000 / 'VHO_F03.DBF'),
str(CENSO2000 / 'VHO_F04.DBF'),
str(CENSO2000 / 'VHO_F05.DBF'),
str(CENSO2000 / 'VHO_F06.DBF'),
str(CENSO2000 / 'VHO_F07.DBF'),
str(CENSO2000 / 'VHO_F08.DBF'),
str(CENSO2000 / 'VHO_F09.DBF'),
str(CENSO2000 / 'VHO_F10.DBF'),
str(CENSO2000 / 'VHO_F11.DBF'),
str(CENSO2000 / 'VHO_F12.DBF'),
str(CENSO2000 / 'VHO_F13.DBF'),
str(CENSO2000 / 'VHO_F14.DBF'),
str(CENSO2000 / 'VHO_F15.DBF'),
str(CENSO2000 / 'VHO_F16.DBF'),
str(CENSO2000 / 'VHO_F17.DBF'),
str(CENSO2000 / 'VHO_F18.DBF'),
str(CENSO2000 / 'VHO_F19.DBF'),
str(CENSO2000 / 'VHO_F20.DBF'),
str(CENSO2000 / 'VHO_F21.DBF'),
str(CENSO2000 / 'VHO_F22.DBF'),
str(CENSO2000 / 'VHO_F23.DBF'),
str(CENSO2000 / 'VHO_F24.DBF'),
str(CENSO2000 / 'VHO_F25.DBF'),
str(CENSO2000 / 'VHO_F26.DBF'),
str(CENSO2000 / 'VHO_F27.DBF'),
str(CENSO2000 / 'VHO_F28.DBF'),
str(CENSO2000 / 'VHO_F29.DBF'),
str(CENSO2000 / 'VHO_F30.DBF'),
str(CENSO2000 / 'VHO_F31.DBF'),
str(CENSO2000 / 'VHO_F32.DBF') ]

paths_ppl = [str(CENSO2000 / 'PER_F01.DBF'),
str(CENSO2000 / 'PER_F02.DBF'),
str(CENSO2000 / 'PER_F03.DBF'),
str(CENSO2000 / 'PER_F04.DBF'),
str(CENSO2000 / 'PER_F05.DBF'),
str(CENSO2000 / 'PER_F06.DBF'),
str(CENSO2000 / 'PER_F07.DBF'),
str(CENSO2000 / 'PER_F08.DBF'),
str(CENSO2000 / 'PER_F09.DBF'),
str(CENSO2000 / 'PER_F10.DBF'),
str(CENSO2000 / 'PER_F11.DBF'),
str(CENSO2000 / 'PER_F12.DBF'),
str(CENSO2000 / 'PER_F13.DBF'),
str(CENSO2000 / 'PER_F14.DBF'),
str(CENSO2000 / 'PER_F15.DBF'),
str(CENSO2000 / 'PER_F16.DBF'),
str(CENSO2000 / 'PER_F17.DBF'),
str(CENSO2000 / 'PER_F18.DBF'),
str(CENSO2000 / 'PER_F19.DBF'),
str(CENSO2000 / 'PER_F20.DBF'),
str(CENSO2000 / 'PER_F21.DBF'),
str(CENSO2000 / 'PER_F22.DBF'),
str(CENSO2000 / 'PER_F23.DBF'),
str(CENSO2000 / 'PER_F24.DBF'),
str(CENSO2000 / 'PER_F25.DBF'),
str(CENSO2000 / 'PER_F26.DBF'),
str(CENSO2000 / 'PER_F27.DBF'),
str(CENSO2000 / 'PER_F28.DBF'),
str(CENSO2000 / 'PER_F29.DBF'),
str(CENSO2000 / 'PER_F30.DBF'),
str(CENSO2000 / 'PER_F31.DBF'),
str(CENSO2000 / 'PER_F32.DBF') ]


   


##We first drag the info of the ppl survey

df2000ppl = df_create( paths_ppl)



## And Create a dummy if someone in the family works in mining
minin_codes = [1102 , 1202 , 5110 , 5111 , 5112 , 5119 , 5210 , 5211 , 5212 , 5213 , 5310 , 5311 , 5410 , 5411]
df2000ppl['OCUACTIV_C'] = df2000ppl.OCUACTIV_C.fillna(0)
df2000ppl['OCUACTIV_C'] = df2000ppl['OCUACTIV_C'].astype(int)
df2000ppl.loc[df2000ppl['OCUACTIV_C'].isin(minin_codes), 'mining'] = 1
df2000ppl['mining'] = df2000ppl.mining.fillna(0)

df2000ppl['ID_VIV'] = df2000ppl.apply(lambda x: str(x['ENT']) + 'm' +str(x['MUN']) + 'v' + str(x['NUMVIV']) + 'n' + str(x['NUMHOG']) , axis=1) 
temp2 = df2000ppl.groupby('ID_VIV')['mining'].max()

##The rest of the data on the head 
df2000ppl = df2000ppl.loc[df2000ppl['OTROPARE_C'].isin([  100]), 
            ['ID_VIV', 'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORTRA', 'ESCOACUM', 
             'OCUACTIV_C', 'SITTRA', 'SERVMED', 'ESTCON', 'VACACION'] ]##Until here are from ppl



#Viv index
df2000 = df_create( paths)
df2000['ID_VIV'] = df2000.apply(lambda x: str(x['ENT']) + 'm' +str(x['MUN']) + 'v' + str(x['NUMVIV']) + 'n' + str(x['NUMHOG']) , axis=1) 

for i in temp2 , df2000ppl :
    df2000 = pd.merge(df2000, i, on= 'ID_VIV' , how = 'inner' )
    del i 

del temp2, df2000ppl

##Matching names of the var
df2000.rename(columns={"SITTRA": "SIT_TRAB", 'HORTRA' : 'HORAS' , 'OCUACTIV_C' : 'CVE_OCUP' ,'CUADORM' : 'P_DORMIR' , 'TOTCUART' : 'T_CUARTOS' , 
                       'CONAGU' : 'CON_AGUA', 'DISAGU' : 'AGUA_ENTU' , 'TENVIV': 'TENENCIA', 'INGTOHOG' : 'INGRESO'}, inplace=True)

#Cleaning and deleting extra columns
df2000= df2000[['ENT', 'MUN', 'ID_VIV', 'FACTOR', 'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORAS', 'ESCOACUM', 'INGRESO','CVE_OCUP', 'SIT_TRAB', 'VACACION', 
                'SERVMED', 'mining', 'CLAVIV' , 'TIPOHOG', 'PAREDES', 'TECHOS', 'PISOS', 'P_DORMIR', 'T_CUARTOS', 'COCINA', 'COCDOR', 
               'SERSAN',  'CON_AGUA', 'AGUA_ENTU', 'DRENAJE', 'ELECTRI', 'COMBUST', 'TENENCIA',
               'TOTPERS', 'ELIBAS', 'RADIO', 'TELEVI', 'VIDEO', 'LICUAD', 'REFRIG', 'LAVADORA', 'TELEFONO', 'BOILER', 'AUTOPROP', 'COMPU' ]]

##Now we generate the dummies and so on 

##For the household info    
dummies( df2000,  'CLAVIV', [1, 2, 3])
dummies( df2000,  'PAREDES', 8)
dummies( df2000,  'TECHOS', [5, 6])
dummies( df2000,  'PISOS', [2, 3])
dummies( df2000,  'COCINA', 1)
dummies( df2000,  'COCDOR', 4)
dummies( df2000,  'SERSAN', 1) #Tiene sanitario
dummies( df2000,  'CON_AGUA', 1)
dummies( df2000,  'AGUA_ENTU', 1 )
dummies( df2000,  'DRENAJE', [1, 2] )
dummies( df2000,  'ELECTRI', 1 )
dummies( df2000,  'COMBUST', [1, 5] )
dummies( df2000,  'ELIBAS', [1, 2] )
dummies( df2000,  'RADIO', 1 )
dummies( df2000,  'TELEVI', 3 )
dummies( df2000,  'VIDEO', 5 )
dummies( df2000,  'LICUAD', 7 )
dummies( df2000,  'REFRIG', 1 )
dummies( df2000,  'LAVADORA', 3 )
dummies( df2000,  'TELEFONO', 5 )
dummies( df2000,  'BOILER', 7 )
dummies( df2000,  'AUTOPROP', 1 )
dummies( df2000,  'COMPU', 3 )
dummies( df2000,  'TENENCIA', 1 )

#For ppl 
dummies( df2000,  'HLENGUA', 1)
dummies( df2000,  'HESPANOL', 3)
dummies( df2000,  'VACACION', 1)

variable = [ 'TIPOHOG' , 'SIT_TRAB' ] #to make dummies

for x in variable :
    data_dummies = pd.get_dummies(df2000[x],prefix=x)
    df2000 = pd.concat([df2000, data_dummies], axis=1)

to_delete = [ "TIPOHOG_9", "SIT_TRAB_9" ]
for i in to_delete:
        try:
            df2000.drop([i], axis=1, inplace=True)
        except:
            pass

df2000.loc[df2000['P_DORMIR'].isin([99]), 'P_DORMIR']= np.nan 
df2000.loc[df2000['T_CUARTOS'].isin([99]), 'T_CUARTOS']= np.nan 
df2000.loc[df2000['EDAD'].isin([999]), 'EDAD']= np.nan 
df2000.loc[df2000['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 


df2000['year']= 2000

df2000 = df2000.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')

df2000.to_csv(str(CENSO2000 / 'data_mexico00.csv'), index = True)

del i, data_dummies, df2000, minin_codes, to_delete, variable, x



paths = [str(CENSO2010 / 'Viviendas_01.dbf'),
str(CENSO2010 / 'Viviendas_02.dbf'),
str(CENSO2010 / 'Viviendas_03.dbf'),
str(CENSO2010 / 'Viviendas_04.dbf'),
str(CENSO2010 / 'Viviendas_05.dbf'),
str(CENSO2010 / 'Viviendas_06.dbf'),
str(CENSO2010 / 'Viviendas_07.dbf'),
str(CENSO2010 / 'Viviendas_08.dbf'),
str(CENSO2010 / 'Viviendas_09.dbf'),
str(CENSO2010 / 'Viviendas_10.dbf'),
str(CENSO2010 / 'Viviendas_11.dbf'),
str(CENSO2010 / 'Viviendas_12.dbf'),
str(CENSO2010 / 'Viviendas_13.dbf'),
str(CENSO2010 / 'Viviendas_14.dbf'),
str(CENSO2010 / 'viviendas_15.dbf'),
str(CENSO2010 / 'Viviendas_16.dbf'),
str(CENSO2010 / 'Viviendas_17.dbf'),
str(CENSO2010 / 'Viviendas_18.dbf'),
str(CENSO2010 / 'Viviendas_19.dbf'),
str(CENSO2010 / 'Viviendas_20.dbf'),
str(CENSO2010 / 'Viviendas_21.dbf'),
str(CENSO2010 / 'Viviendas_22.dbf'),
str(CENSO2010 / 'Viviendas_23.dbf'),
str(CENSO2010 / 'Viviendas_24.dbf'),
str(CENSO2010 / 'Viviendas_25.dbf'),
str(CENSO2010 / 'Viviendas_26.dbf'),
str(CENSO2010 / 'Viviendas_27.dbf'),
str(CENSO2010 / 'Viviendas_28.dbf'),
str(CENSO2010 / 'Viviendas_29.dbf'),
str(CENSO2010 / 'Viviendas_30.dbf'),
str(CENSO2010 / 'Viviendas_31.dbf'),
str(CENSO2010 / 'Viviendas_32.dbf') ]

paths_ppl = [str(CENSO2010 / 'Personas_01.dbf'),
str(CENSO2010 / 'Personas_02.dbf'),
str(CENSO2010 / 'Personas_03.dbf'),
str(CENSO2010 / 'Personas_04.dbf'),
str(CENSO2010 / 'Personas_05.dbf'),
str(CENSO2010 / 'Personas_06.dbf'),
str(CENSO2010 / 'Personas_07.dbf'),
str(CENSO2010 / 'Personas_08.dbf'),
str(CENSO2010 / 'Personas_09.dbf'),
str(CENSO2010 / 'Personas_10.dbf'),
str(CENSO2010 / 'Personas_11.dbf'),
str(CENSO2010 / 'Personas_12.dbf'),
str(CENSO2010 / 'Personas_13.dbf'),
str(CENSO2010 / 'Personas_14.dbf'),
str(CENSO2010 / 'personas_15.dbf'),
str(CENSO2010 / 'Personas_16.dbf'),
str(CENSO2010 / 'Personas_17.dbf'),
str(CENSO2010 / 'Personas_18.dbf'),
str(CENSO2010 / 'Personas_19.dbf'),
str(CENSO2010 / 'Personas_20.dbf'),
str(CENSO2010 / 'Personas_21.dbf'),
str(CENSO2010 / 'Personas_22.dbf'),
str(CENSO2010 / 'Personas_23.dbf'),
str(CENSO2010 / 'Personas_24.dbf'),
str(CENSO2010 / 'Personas_25.dbf'),
str(CENSO2010 / 'Personas_26.dbf'),
str(CENSO2010 / 'Personas_27.dbf'),
str(CENSO2010 / 'Personas_28.dbf'),
str(CENSO2010 / 'Personas_29.dbf'),
str(CENSO2010 / 'Personas_30.dbf'),
str(CENSO2010 / 'Personas_31.dbf'),
str(CENSO2010 / 'Personas_32.dbf')]

##We first drag the info of the ppl survey  THIS FUCKING SHUT IS ENCODED DIFFERENTLY

import geopandas as gpd 
def df2010_create(y):
    db=pd.DataFrame() 
    for x in y :
        temp = gpd.read_file(x)
        temp = pd.DataFrame(temp)
        db = pd.concat([db, temp], axis=0)
    for i in list(db.columns):
            try:
                db[i] = db[i].astype(int)
            except:
                pass
    return(db)

df2010ppl = df2010_create( paths_ppl)

## And Create a dummy if someone in the family works in mining
minin_codes = [2254 , 1312 , 1612 , 2623 , 7111 , 8111 , 9211 ]  

df2010ppl['OCUACTIV_C'] = df2010ppl.OCUACTIV_C.fillna(0)
df2010ppl['OCUACTIV_C'] = df2010ppl['OCUACTIV_C'].astype(int)
df2010ppl.loc[df2010ppl['OCUACTIV_C'].isin(minin_codes), 'mining'] = 1
df2010ppl['mining'] = df2010ppl.mining.fillna(0)


temp2 = df2010ppl.groupby('ID_VIV')['mining'].max()

##The rest of the data on the head 
df2010ppl = df2010ppl.loc[df2010ppl['PARENT'].isin([  1]), 
            ['ID_VIV', 'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORTRA', 'ESCOACUM', 
             'OCUACTIV_C', 'SITTRA', 'PRESLAB1', 'ESTCON', 'PRESLAB3'] ]##Until here are from ppl

#Viv index
df2010 = df2010_create( paths)

for i in temp2 , df2010ppl :
    df2010 = pd.merge(df2010, i, on= 'ID_VIV' , how = 'inner' )
    del i 

del temp2, df2010ppl  

#Renaming to make compatible and to reducing the sample size

df2010.rename(columns={"SITTRA": "SIT_TRAB", 'HORTRA' : 'HORAS' , 'OCUACTIV_C' : 'CVE_OCUP' , 'INGTRHOG' : 'INGRESOS',
                       'PRESLAB1': 'SERVMED' , 'PRESLAB3': 'VACACION' , 'CLAVIVP' : 'CLAVIV' ,                       
                       'CUADORM' : 'P_DORMIR' , 'TOTCUART' : 'T_CUARTOS' , 
                       'CONAGU' : 'CON_AGUA', 'DISAGU' : 'AGUA_ENTU' , 'TENVIV': 'TENENCIA', 
                       'NUMPERS' : 'TOTPERS' }, inplace=True)

df2010= df2010[['ENT', 'MUN', 'ID_VIV', 'FACTOR' ,'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORAS', 'ESCOACUM', 'INGRESOS', 'CVE_OCUP', 'SERVMED', 
                'SIT_TRAB', 'VACACION', 'mining', 'CLAVIV' , 'TIPOHOG', 'PAREDES', 'TECHOS', 'PISOS', 'P_DORMIR', 'T_CUARTOS', 'COCINA',  
               'SERSAN',  'CON_AGUA', 'AGUA_ENTU', 'DRENAJE', 'ELECTRI', 'COMBUST', 'TENENCIA',
               'TOTPERS', 'ELIBAS', 'RADIO', 'TELEVI', 'INTERNET', 'REFRIG', 'LAVADORA', 'TELEFONO', 'BOILER', 'AUTOPROP', 'COMPU' ]]

columns = ['HLENGUA', 'HESPANOL', 'HORAS', 'ESCOACUM', 'INGRESOS', 'CVE_OCUP', 'SERVMED', 
       'VACACION', 'CLAVIV', 'PAREDES', 'TECHOS', 'PISOS','P_DORMIR', 'T_CUARTOS', 'COCINA', 'SERSAN', 'CON_AGUA', 'AGUA_ENTU',
       'DRENAJE', 'ELECTRI', 'COMBUST', 'TENENCIA', 'TOTPERS', 'ELIBAS',
       'RADIO', 'TELEVI', 'INTERNET', 'REFRIG', 'LAVADORA', 'TELEFONO', 'BOILER', 'AUTOPROP', 'COMPU']

for i in columns:
    df2010[i] = pd.to_numeric(df2010[i], errors='coerce', downcast='integer')
    
#Now we encode 
##For the household info    
dummies( df2010,  'CLAVIV', [1, 2, 3])
dummies( df2010,  'PAREDES', 8)
dummies( df2010,  'TECHOS', [8, 9])
dummies( df2010,  'PISOS', [2, 3])
dummies( df2010,  'COCINA', 1)
dummies( df2010,  'SERSAN', 1) #Tiene sanitario
dummies( df2010,  'CON_AGUA', 5)
dummies( df2010,  'AGUA_ENTU', 1 )
dummies( df2010,  'DRENAJE', [1, 2] )
dummies( df2010,  'ELECTRI', 1 )
dummies( df2010,  'COMBUST', [1, 2, 5] )
dummies( df2010,  'ELIBAS', [1, 3] )
dummies( df2010,  'RADIO', 1 )
dummies( df2010,  'TELEVI', 3 )
dummies( df2010,  'INTERNET', 1 )
dummies( df2010,  'REFRIG', 1 )
dummies( df2010,  'LAVADORA', 3 )
dummies( df2010,  'TELEFONO', 1 )
dummies( df2010,  'BOILER', 3 )
dummies( df2010,  'AUTOPROP', 1 )
dummies( df2010,  'COMPU', 3 )

#For ppl 
dummies( df2010,  'HLENGUA', 1)
dummies( df2010,  'HESPANOL', 1)
dummies( df2010,  'VACACION', 1)
dummies( df2010,  'SERVMED', 1)

variable = [ 'TIPOHOG' , 'SIT_TRAB' ,  'TENENCIA'] #to make dummies

for x in variable :
    data_dummies = pd.get_dummies(df2010[x],prefix=x)
    df2010 = pd.concat([df2010, data_dummies], axis=1)

to_delete = [ "TIPOHOG_9", "SIT_TRAB_9" , 'TENENCIA_3' , 'TENENCIA_9']
for i in to_delete:
        try:
            df2010.drop([i], axis=1, inplace=True)
        except:
            pass

df2010.loc[df2010['P_DORMIR'].isin([99]), 'P_DORMIR']= np.nan 
df2010.loc[df2010['T_CUARTOS'].isin([99]), 'T_CUARTOS']= np.nan 
df2010.loc[df2010['EDAD'].isin([999]), 'EDAD']= np.nan 
df2010.loc[df2010['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
df2010.loc[df2010['INGRESOS'].isin([999999]), 'INGRESOS']= np.nan 


df2010['year']= 2010

df2010.to_csv(str(CENSO2010 / 'data_mexico10.csv'), index = True)

del i, data_dummies, df2010, minin_codes, to_delete, variable, x



## Path of the census data 
path_c2020_viviendas= str(CENSO2020 / 'Viviendas00.CSV')
path_c2020_personas= str(CENSO2020 / 'Personas00.CSV')

df2020ppl=pd.read_csv(path_c2020_personas)

## And Create a dummy if someone in the family works in mining
minin_codes = [225 , 262, 811, 921 ]  


df2020ppl['OCUPACION_C'] = df2020ppl.OCUPACION_C.fillna(0)
df2020ppl['OCUPACION_C'] = df2020ppl['OCUPACION_C'].astype(int)
df2020ppl.loc[df2020ppl['OCUPACION_C'].isin(minin_codes), 'mining'] = 1
df2020ppl['mining'] = df2020ppl.mining.fillna(0)


temp2 = df2020ppl.groupby('ID_VIV')['mining'].max()

##The rest of the data on the head 

df2020ppl = df2020ppl.loc[df2020ppl['PARENTESCO'].isin([101]), 
            ['ID_VIV', 'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORTRA', 'ESCOACUM', 
             'OCUPACION_C', 'SITTRA', 'SERVICIO_MEDICO', 'SITUA_CONYUGAL', 'VACACIONES'] ]##Until here are from ppl

#Viv index
df2020 = pd.read_csv(path_c2020_viviendas)

for i in temp2 , df2020ppl :
    df2020 = pd.merge(df2020, i, on= 'ID_VIV' , how = 'inner' )
    del i 

del temp2, df2020ppl  

#Renaming to make compatible and to reducing the sample size

df2020.rename(columns={"SITTRA": "SIT_TRAB", 'HORTRA' : 'HORAS' , 'OCUPACION_C' : 'CVE_OCUP' , 'INGTRHOG' : 'INGRESOS',
                       'SERVICIO_MEDICO': 'SERVMED' , 'VACACIONES': 'VACACION' , 'CLAVIVP' : 'CLAVIV' ,                       
                       'CUADORM' : 'P_DORMIR' , 'TOTCUART' : 'T_CUARTOS' , 'ELECTRICIDAD' : 'ELECTRI',
                       'COMBUSTIBLE' : 'COMBUST', 'DESTINO_BAS' : 'ELIBAS', 'REFRIGERADOR':'REFRIG' ,
                       'CONAGUA' : 'CON_AGUA', 'AGUA_ENTUBADA' : 'AGUA_ENTU' , 'TELEVISOR' : 'TELEVI',
                         'COMPUTADORA' : 'COMPU', 'NUMPERS' : 'TOTPERS' }, inplace=True)


df2020= df2020[['ENT', 'MUN', 'ID_VIV', 'FACTOR' ,'SEXO', 'EDAD', 'HLENGUA', 'HESPANOL', 'HORAS', 'ESCOACUM', 'INGRESOS','CVE_OCUP', 'SERVMED', 'SIT_TRAB', 'VACACION', 'mining',
                'CLAVIV' , 'TIPOHOG', 'PAREDES', 'TECHOS', 'PISOS', 'P_DORMIR', 'T_CUARTOS', 'COCINA',  
               'SERSAN',  'CON_AGUA', 'AGUA_ENTU', 'DRENAJE', 'ELECTRI', 'COMBUST', 'TENENCIA',
               'TOTPERS', 'ELIBAS', 'RADIO', 'TELEVI', 'INTERNET', 'REFRIG', 'LAVADORA', 'TELEFONO', 'BOILER', 'AUTOPROP', 'COMPU' ]]

#Now we encode 
##For the household info    
dummies( df2020,  'CLAVIV', [1, 2, 3, 4, 5])
dummies( df2020,  'PAREDES', 8)
dummies( df2020,  'TECHOS', [5, 9, 10])
dummies( df2020,  'PISOS', [2, 3])
dummies( df2020,  'COCINA', 1)
dummies( df2020,  'SERSAN', 1) #Tiene sanitario
dummies( df2020,  'CON_AGUA', 1)
dummies( df2020,  'AGUA_ENTU', 1 )
dummies( df2020,  'DRENAJE', [1, 2] )
dummies( df2020,  'ELECTRI', 1 )
dummies( df2020,  'COMBUST', [2, 3] )
dummies( df2020,  'ELIBAS', [1, 2] )
dummies( df2020,  'RADIO', 5 )
dummies( df2020,  'TELEVI', 7 )
dummies( df2020,  'INTERNET', 7 )
dummies( df2020,  'REFRIG', 1 )
dummies( df2020,  'LAVADORA', 3 )
dummies( df2020,  'TELEFONO', 3 )
dummies( df2020,  'BOILER', 1 )
dummies( df2020,  'AUTOPROP', 7 )
dummies( df2020,  'COMPU', 1 )

#For ppl 
dummies( df2020,  'HLENGUA', 1)
dummies( df2020,  'HESPANOL', 1)
dummies( df2020,  'VACACION', 3)
dummies( df2020,  'SERVMED', 5)


df2020.loc[df2020['P_DORMIR'].isin([99]), 'P_DORMIR']= np.nan 
df2020.loc[df2020['T_CUARTOS'].isin([99]), 'T_CUARTOS']= np.nan 
df2020.loc[df2020['EDAD'].isin([999]), 'EDAD']= np.nan 
df2020.loc[df2020['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
df2020.loc[df2020['INGRESOS'].isin([999999]), 'INGRESOS']= np.nan 

variable = [ 'TIPOHOG' , 'SIT_TRAB' ,  'TENENCIA'] #to make dummies

for x in variable :
    data_dummies = pd.get_dummies(df2020[x],prefix=x)
    df2020 = pd.concat([df2020, data_dummies], axis=1)

to_delete = [ "TIPOHOG_9", "SIT_TRAB_9" , 'TENENCIA_3' , 'TENENCIA_4' ,'TENENCIA_9']
for i in to_delete:
        try:
            df2020.drop([i], axis=1, inplace=True)
        except:
            pass

df2020['year']= 2020

df2020.to_csv(str(CENSO2020 / 'data_mexico20.csv'), index = True)

del i, data_dummies, df2020, minin_codes, to_delete, variable, x

### I NEED TO PUT THE IDENTIFIER  CVEGEO ALL THE DATASETS.... THE PROBLEM THAT THE 2 LAST ARE WAY TO HEAVY 

#For 2010

df2010 = str(CENSO2010 / 'data_mexico10.csv')
df2010= pd.read_csv(df2010)

df2010 = df2010.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
df2010.to_csv(str(CENSO2010 / 'data_mexico10.csv'), index = True)
del df2010

#For 2020
df2020 = str(CENSO2020 / 'data_mexico20.csv')
df2020= pd.read_csv(df2020)

df2020 = df2020.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
df2020.to_csv(str(CENSO2020 / 'data_mexico20.csv'), index = True)
del df2020


import pandas as pd
import numpy as np


minex_path= str(CENSO2020 / 'Minex_data.csv')


minex = pd.read_csv(minex_path)


##We keep mexico only

minex = minex[minex.Country == 'Mexico']

##We construct dummies for the info need it 
minex.rename(columns = {'Contained':'Contained_Commodities', 'Current St':'Current_Status', 'Mine Shutd' : 'Mine_close',
                        'Primary Me':'Primary_Metal' , 'Mine Start': 'Mine_start', 	'CVEGEO' : 'Mun_location'}, inplace = True)

minex =minex[['ID No','Size', 'Primary_Metal' , 'Contained_Commodities', 'Current_Status', 
              'Discovery', 'Mine_start', 'Mine_close', 'Mun_location' ]] ##'Contained Commodities', 'Current Status'


to_dummies = ['Primary_Metal', 'Size' ]

for x in to_dummies :
    data_dummies = pd.get_dummies(minex[x],prefix=x)
    minex = pd.concat([minex, data_dummies], axis=1)
    del data_dummies
    
##Also for the minerals extracted in a given mine    
unique_commodities= ['Cu',  #cobre etm
                     'Au', #Oro  precious
                     'C_graphite', #Grafito  mineral
                     'Fe', #Iron metal
                     'Li', #Lithium   etm  
                     'Mn', #Manganese etm
                     'Mo', # Mineral
                     'Ag', # plata  precious
                     'W', #metal
                     'Zn', #zinc etm
                     'Calc', #other
                     'K', #potassium mineral
                     'Pb', # Lead etm
                     'REE', # etm
                     'Sb', # other
                     'Ay', # other
                     'Clays' ]  #other

precious = ['Au', 'Ag']
etm = [ 'Cu', 'Li','Mn', 'Zn', 'Pb', 'REE' ]
other_contained = ['C_graphite', 'Fe', 'Mo', 'W', 'Calc', 'K', 'Sb', 'Ay', 'Clays' ]

minex['Contain_precious'] = minex.apply(lambda row: float(any(x in row['Contained_Commodities'] for x in precious) )  , axis=1 )
minex['Contain_etm'] = minex.apply(lambda row: float(any(x in row['Contained_Commodities'] for x in etm) )  , axis=1 )
minex['Contain_other'] = minex.apply(lambda row: float(any(x in row['Contained_Commodities'] for x in other_contained) )  , axis=1 )

##And for status of the mines
     ## minex['Current Status'].value_counts()
Operating = ["Operating Mine", "Operating Mine - unsure if still operating", "Past Producer - Reopened"]
Exploration = ["Advanced Exploration", 'Exploration']
Feasibility = ["Pre-Feas/Scoping", "Feasibility Study - New project", 'Feasibility Study ',   ]
Closed = ["Closed Mine", 'closed Mine']
Stalled = ["Advanced Exploration - Failed to progress", 'Feasibility Study - Stalled (economic)', 
           "Feasibility Study - Stalled (environmental)",  "Feasibility Study - Stalled", 
           'Advanced Exploration - Failed to Progress ', 'Pre-Feas/Scoping - Failed to progress', 
           'Pre-Feas/Scoping - Stalled (economic)']
Other_status = ["Development/Construction", "Advanced Exploration - Old mine", "Undeveloped Deposit", 
                'Care and Maintenance', 'Prospect' ]
  
minex['Operating'] = minex.apply(lambda row: float(row['Current_Status'] in Operating )  , axis=1 )
minex['Exploration'] = minex.apply(lambda row: float(row['Current_Status'] in Exploration )  , axis=1 )
minex['Feasibility'] = minex.apply(lambda row: float(row['Current_Status'] in Feasibility )  , axis=1 )
minex['Closed'] = minex.apply(lambda row: float(row['Current_Status'] in Closed )  , axis=1 )
minex['Stalled'] = minex.apply(lambda row: float(row['Current_Status'] in Stalled )  , axis=1 )
minex['Other_status'] = minex.apply(lambda row: float(row['Current_Status'] in Other_status )  , axis=1 )

del unique_commodities, precious, etm, other_contained, Operating, Feasibility, Closed, Stalled, Other_status, to_dummies, x, Exploration


## Generating FE for year of discovery and year that start operating 

def algo(x, tipo) :
    if type(x) == str :
         z= tipo(map(int , x.split(',')))
         
    if type(x)== float :
        z= float(x)
    return(z)
        
minex['Start_year1'] = minex.apply(lambda row: algo(row['Mine_start'], min)  , axis=1 )
minex['Start_year2'] = minex.apply(lambda row: algo(row['Mine_start'], max)  , axis=1 )
minex['Close_year1'] = minex.apply(lambda row: algo(row['Mine_close'], min)  , axis=1 )
minex['Close_year2'] = minex.apply(lambda row: algo(row['Mine_close'], max)  , axis=1 )

minex.loc[minex['Start_year1'] == minex['Start_year2'], 'Start_year2'] = np.nan
minex.loc[minex['Close_year1'] == minex['Close_year2'], 'Close_year2'] = np.nan

#fixing a couple of dates 
minex.loc[minex['ID No'] == 61331, 'Start_year1'] = 2011
minex.loc[minex['ID No'] == 33788, 'Start_year1'] = 1995  

##For Chaisemartin we need the number of mines per municipality per year for the treatment 

minex['mining1990'] = minex.apply(lambda row: int(row['Start_year1']<=1990 and (row['Close_year1']>1990 or pd.isna(row['Close_year1']))) , axis=1 )  

minex['mining2000'] = minex.apply(lambda row: int((row['Start_year1']<=2000 and (row['Close_year1']>2000 or pd.isna(row['Close_year1'])))
                                                  or (row['Start_year2']<=2000))    , axis=1 )    

minex['mining2010'] = minex.apply(lambda row: int((row['Start_year1']<=2010 and (row['Close_year1']>2010 or pd.isna(row['Close_year1'])))
                                                  or (row['Start_year2']<=2010))    , axis=1 )   
minex['mining2020'] = minex.apply(lambda row: int((row['Start_year1']<=2020 and (row['Close_year1']>2020 or pd.isna(row['Close_year1'])))
                                                  or (row['Start_year2']<=2020))    , axis=1 )   

minex.loc[minex['ID No'] == 33839, 'mining2020'] = 0 #one mine closes again

##And we kind of do the same for discovery
minex['discovery1990'] = minex.apply(lambda row: int(row['Discovery']<=1990) , axis=1 )  

minex['discovery2000'] = minex.apply(lambda row: int(row['Discovery']<=2000)    , axis=1 )    

minex['discovery2010'] = minex.apply(lambda row: int(row['Discovery']<=2010 )    , axis=1 )   
minex['discovery2020'] = minex.apply(lambda row: int(row['Discovery']<=2020 )    , axis=1 )   

######################################################
#
#For different tests on particular types of mines
#
#######################################################


##Then we create the neighbors treated group based on dummies 
agg_func = {'CVE_ENT': 'max', 'CVE_MUN': 'max', 'ID No': 'count', 'Size': 'first', 'Primary_Metal': 'first',
       'Contained_Commodities': 'first', 'Current_Status': 'first', 'Discovery': 'min', 'Mine_start': 'first',
       'Mine_close': 'first', 'Mun_location': 'first', 'Primary_Metal_Copper': 'max',
       'Primary_Metal_Gold': 'max', 'Primary_Metal_Graphite': 'max',
       'Primary_Metal_Iron Ore': 'max', 'Primary_Metal_Lithium': 'max',
       'Primary_Metal_Manganese': 'max', 'Primary_Metal_Molybdenum': 'max',
       'Primary_Metal_Silver': 'max', 'Primary_Metal_Tungsten': 'max', 'Primary_Metal_Zinc': 'max',
       'Size_Giant': 'max', 'Size_Major': 'max', 'Size_Moderate': 'max', 'Contain_precious': 'max',
       'Contain_etm': 'max', 'Contain_other': 'max', 'Operating': 'max', 'Exploration': 'max',
       'Feasibility': 'max', 'Closed': 'max', 'Stalled': 'max', 'Other_status': 'max', 'Start_year1': 'min',
       'Start_year2': 'min', 'Close_year1': 'min', 'Close_year2' : 'min', 'mining1990': 'sum','mining2000': 'sum' , 'mining2010': 'sum', 'mining2020': 'sum',
       'discovery1990': 'sum','discovery2000': 'sum' , 'discovery2010': 'sum', 'discovery2020': 'sum',
    }

for x in [5, 10, 15, 20, 25, 30, 40, 50, 75, 100 ] :
   mona = pd.read_excel(str(CENSO2020 / 'Maps_data' / 'Intersection_')+str(x)+".xlsx")
   mona = mona.merge(right = minex, how = 'left', on = 'ID No')
   mona = mona.groupby('CVEGEO').agg(agg_func)
   mona = mona[['CVE_ENT', 'CVE_MUN', 'ID No', 'Discovery', 'Mun_location', 'Primary_Metal_Copper',
       'Primary_Metal_Gold', 'Primary_Metal_Graphite', 'Primary_Metal_Iron Ore', 'Primary_Metal_Lithium',
       'Primary_Metal_Manganese', 'Primary_Metal_Molybdenum',
       'Primary_Metal_Silver', 'Primary_Metal_Tungsten', 'Primary_Metal_Zinc',
       'Size_Giant', 'Size_Major', 'Size_Moderate', 'Contain_precious',
       'Contain_etm', 'Contain_other', 'Operating', 'Exploration',
       'Feasibility', 'Closed', 'Stalled', 'Other_status', 'Start_year1',
       'Start_year2', 'Close_year1', 'Close_year2' , 'mining1990', 'mining2000', 'mining2010' , 'mining2020' ,
       'discovery1990', 'discovery2000', 'discovery2010' , 'discovery2020'    ]]
   mona.rename(columns = {'ID No':'No_mines'}, inplace=(True))
   mona.to_csv(str(CORE / ('neighbors'+str(x)+'.csv')), index = True)
   del mona

## ADDITIONALLY WE NEED THE DATA OF municipality things 

## Adding aditional Variables of municipality 
municipalities = str(CENSO2020 / 'Municipalities info.csv')
mex_info= pd.read_csv(municipalities)

# 1) Distance to state capital 
mex_info.rename(columns = {'distance':'Dist_Capital'}, inplace = True)
mex_info.loc[mex_info.CVE_ENT==9, 'Dist_Capital'] = 0

# 2) LAND USE 
land_path = str(CENSO2020 / 'LandUse_Municipality.csv')
land =  pd.read_csv(land_path)
land = land[['CVEGEO', 'CLAVE', 'area']] 
land = pd.pivot_table(land, values = 'area', index = ['CVEGEO'], columns=['CLAVE'], aggfunc = np.sum, fill_value=0) #Turning the sum of the area in columns 

##making area of agriculture and area of human settlement 
land2 = pd.DataFrame(land['AH'])
land2 = land2.reset_index()
land.drop ('AH', inplace=True , axis=1)
land = pd.DataFrame(land.agg("sum", axis="columns"))
land = land.reset_index()
land = land.merge(right = land2, how = 'inner', on = 'CVEGEO')
land.columns = ['CVEGEO', 'Agricultural', 'Human_settle']

mex_info = mex_info.merge(land, on = 'CVEGEO', how = 'outer')

mex_info['agro_land'] = mex_info['Agricultural']/ mex_info['area']
mex_info['human_land'] = mex_info['Human_settle']/ mex_info['area']

## 3) Fiscal revenue of municipalities

fiscal_path = str(CENSO2020 / 'Inegi Fiscal income.xls')
fiscal= pd.read_excel(fiscal_path, usecols= 'A:AK' , header = 4)
fiscal.columns = [       'Index',   'Department',   'Unnamed: 2', 'Municipality',
                 'Income1989',           'Income1990',           'Income1991',           'Income1992',
                 'Income1993',           'Income1994',           'Income1995',           'Income1996',
                 'Income1997',           'Income1998',           'Income1999',           'Income2000',
                 'Income2001',           'Income2002',           'Income2003',           'Income2004',
                 'Income2005',           'Income2006',           'Income2007',           'Income2008',
                 'Income2009',           'Income2010',           'Income2011',           'Income2012',
                 'Income2013',           'Income2014',           'Income2015',           'Income2016',
                 'Income2017',           'Income2018',           'Income2019',           'Income2020',
                 'Income2021']

#Dropping subtotals 
fiscal = fiscal.sort_values(by=['Department', 'Municipality' , 'Income2020'], ascending = True) #Sort the data so that the lowest value is first
fiscal = fiscal.drop_duplicates(subset=['Department', 'Municipality'], keep='first')  #Remove the second value(which will be the subtotal)
fiscal['average90'] = fiscal.loc[:, 'Income1989':'Income1990'].mean(axis=1)
fiscal['average00'] = fiscal.loc[:, 'Income1991':'Income2000'].mean(axis=1)
fiscal['average10'] = fiscal.loc[:, 'Income2001':'Income2010'].mean(axis=1)
fiscal['average20'] = fiscal.loc[:, 'Income2011':'Income2020'].mean(axis=1)

fiscal = fiscal[['Department', 'Municipality', 'Income1990', 'Income2000' , 'Income2010' , 'Income2019' ,'Income2020',
                 'average90', 'average00' , 'average10' , 'average20']]
mex_info = mex_info.merge(fiscal, how= 'left', left_on= ['CVE_ENT', 'NOMGEO'], right_on= [ 'Department', 'Municipality'])
mex_info.drop(['Department', 'Municipality'], inplace=True, axis=1)


mex_info.to_csv(str(CORE / 'mex_info.csv'), index = True)

del fiscal , fiscal_path, land, land2, land_path, municipalities   


###### LASTLY WE NEED ENROLLMENT 


##For 1990 
paths = [str(CENSO1990 / 'm_1001.dbf'),
str(CENSO1990 / 'm_1002.dbf'),
str(CENSO1990 / 'm_1003.dbf'),
str(CENSO1990 / 'm_1004.dbf'),
str(CENSO1990 / 'm_1005.dbf'),
str(CENSO1990 / 'm_1006.dbf'),
str(CENSO1990 / 'm_1007.dbf'),
str(CENSO1990 / 'm_1008.dbf'),
str(CENSO1990 / 'm_1009.dbf'),
str(CENSO1990 / 'm_1010.dbf'),
str(CENSO1990 / 'm_1011.dbf'),
str(CENSO1990 / 'm_1012.dbf'),
str(CENSO1990 / 'm_1013.dbf'),
str(CENSO1990 / 'm_1014.dbf'),
str(CENSO1990 / 'm_1015.dbf'),
str(CENSO1990 / 'm_1016.dbf'),
str(CENSO1990 / 'm_1017.dbf'),
str(CENSO1990 / 'm_1018.dbf'),
str(CENSO1990 / 'm_1019.dbf'),
str(CENSO1990 / 'm_1020.dbf'),
str(CENSO1990 / 'm_1021.dbf'),
str(CENSO1990 / 'm_1022.dbf'),
str(CENSO1990 / 'm_1023.dbf'),
str(CENSO1990 / 'm_1024.dbf'),
str(CENSO1990 / 'm_1025.dbf'),
str(CENSO1990 / 'm_1026.dbf'),
str(CENSO1990 / 'm_1027.dbf'),
str(CENSO1990 / 'm_1028.dbf'),
str(CENSO1990 / 'm_1029.dbf'),
str(CENSO1990 / 'm_1030.dbf'),
str(CENSO1990 / 'm_1031.dbf'),
str(CENSO1990 / 'm_1032.dbf') ]

import numpy as np
from simpledbf import Dbf5

def df_create(y):
    db=pd.DataFrame() 
    for x in y :
        temp = Dbf5(x)
        temp = temp.to_dataframe()
        db = pd.concat([db, temp], axis=0)
    for i in list(db.columns):
            try:
                db[i] = db[i].astype(int)
            except:
                pass
    return(db)
        #del temp 

### Cleaning the data 
#print(df1990.columns)

df1990 = df_create( paths )

## Creating enrollment 

school1990 = df1990.loc[df1990['ANO_CUMP'].isin([  15, 16, 17]), 
            ['ENT', 'MUN', 'SEXO', 'ANO_CUMP', 'ASISTE','APROBO', 'PRESCO',
            'TEC_PRIM', 'TEC_SEC', 'NOR_BAS', 'NIV_EST', 'ANO_APRO']]

school1990.loc[school1990['ANO_APRO'].isin([999]), 'ANO_APRO']= np.nan 

school1990 = school1990.reset_index()
df1990 = df1990.reset_index()
df1990.loc[df1990['NIV_EST'].isin([0] ), 'ESCOACUM']= 0
df1990.loc[df1990['NIV_EST'].isin([1] ), 'ESCOACUM'] = df1990['ANO_APRO']
df1990.loc[df1990['NIV_EST'].isin([2] ), 'ESCOACUM']= df1990['ANO_APRO']+6
df1990.loc[df1990['NIV_EST'].isin([3] ), 'ESCOACUM']= df1990['ANO_APRO']+9 
df1990.loc[df1990['NIV_EST'].isin([4] ), 'ESCOACUM']= df1990['ANO_APRO']+12
df1990.loc[df1990['NIV_EST'].isin([5] ), 'ESCOACUM']= df1990['ANO_APRO']+16

school1990 = school1990.groupby(['ENT', 'MUN']).agg({'ASISTE': lambda x: sum(x == 1), 'ANO_CUMP': 'count'}).reset_index()

school1990.rename(columns={"ANO_CUMP": "COUNT_PPL"}, inplace=True)
school1990['ENROLL_RATE'] = school1990['ASISTE'] / school1990['COUNT_PPL']

#Years of schooling only for adults D:
df1990 = df1990.loc[df1990['ANO_CUMP']>=18, ['ENT', 'MUN', 'ESCOACUM']]   
df1990 = df1990.groupby(['ENT', 'MUN']).agg({ 'ESCOACUM': 'mean'}).reset_index()
school1990 = school1990.merge(df1990, on=(['ENT', 'MUN']), how= 'left')
school1990['YEAR'] = 1990
municipalities = str(CENSO2020 / 'Municipalities info.csv')
mex_info= pd.read_csv(municipalities)

school1990 = school1990.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
school1990 = school1990[['ENT', 'MUN', 'CVEGEO', 'YEAR','ASISTE', 'COUNT_PPL', 'ENROLL_RATE', 'ESCOACUM' ]]
school1990.to_csv(str(CENSO1990 / 'school90.csv'), index = True)
del school1990,  df1990

##For 2000

paths_ppl = [str(CENSO2000 / 'PER_F01.DBF'),
str(CENSO2000 / 'PER_F02.DBF'),
str(CENSO2000 / 'PER_F03.DBF'),
str(CENSO2000 / 'PER_F04.DBF'),
str(CENSO2000 / 'PER_F05.DBF'),
str(CENSO2000 / 'PER_F06.DBF'),
str(CENSO2000 / 'PER_F07.DBF'),
str(CENSO2000 / 'PER_F08.DBF'),
str(CENSO2000 / 'PER_F09.DBF'),
str(CENSO2000 / 'PER_F10.DBF'),
str(CENSO2000 / 'PER_F11.DBF'),
str(CENSO2000 / 'PER_F12.DBF'),
str(CENSO2000 / 'PER_F13.DBF'),
str(CENSO2000 / 'PER_F14.DBF'),
str(CENSO2000 / 'PER_F15.DBF'),
str(CENSO2000 / 'PER_F16.DBF'),
str(CENSO2000 / 'PER_F17.DBF'),
str(CENSO2000 / 'PER_F18.DBF'),
str(CENSO2000 / 'PER_F19.DBF'),
str(CENSO2000 / 'PER_F20.DBF'),
str(CENSO2000 / 'PER_F21.DBF'),
str(CENSO2000 / 'PER_F22.DBF'),
str(CENSO2000 / 'PER_F23.DBF'),
str(CENSO2000 / 'PER_F24.DBF'),
str(CENSO2000 / 'PER_F25.DBF'),
str(CENSO2000 / 'PER_F26.DBF'),
str(CENSO2000 / 'PER_F27.DBF'),
str(CENSO2000 / 'PER_F28.DBF'),
str(CENSO2000 / 'PER_F29.DBF'),
str(CENSO2000 / 'PER_F30.DBF'),
str(CENSO2000 / 'PER_F31.DBF'),
str(CENSO2000 / 'PER_F32.DBF') ]

##We first drag the info of the ppl survey

df2000ppl = df_create( paths_ppl)

columns = ['SEXO', 'EDAD', 'ASISTEN', 'ESCOACUM']

for i in columns:
    df2000ppl[i] = pd.to_numeric(df2000ppl[i], errors='coerce', downcast='integer')

school2000 = df2000ppl.loc[df2000ppl['EDAD'].isin([  15, 16, 17]), 
            ['ENT', 'MUN', 'FACTOR','SEXO', 'EDAD', 'ASISTEN', 'ESCOACUM']]

school2000 = school2000.reset_index()


df2000ppl.loc[df2000ppl['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
school2000.loc[school2000['ASISTEN'].isin([2, 9]), 'ASISTEN']= 0
school2000 = school2000.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ENROLL_RATE': (x['ASISTEN'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()

df2000ppl = df2000ppl.loc[df2000ppl['EDAD']>=18, ['ENT', 'MUN', 'FACTOR','ESCOACUM']]   
df2000ppl = df2000ppl.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ESCOACUM': (x['ESCOACUM'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()
school2000 = school2000.merge(df2000ppl, on=(['ENT', 'MUN']), how= 'left')

school2000['YEAR'] = 2000

school2000 = school2000.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
school2000 = school2000[['ENT', 'MUN', 'CVEGEO', 'YEAR','ENROLL_RATE', 'ESCOACUM' ]]
school2000.to_csv(str(CENSO2000 / 'school00.csv'), index = True)
del school2000,  df2000ppl


##For 2010

paths_ppl = [str(CENSO2010 / 'Personas_01.dbf'),
str(CENSO2010 / 'Personas_02.dbf'),
str(CENSO2010 / 'Personas_03.dbf'),
str(CENSO2010 / 'Personas_04.dbf'),
str(CENSO2010 / 'Personas_05.dbf'),
str(CENSO2010 / 'Personas_06.dbf'),
str(CENSO2010 / 'Personas_07.dbf'),
str(CENSO2010 / 'Personas_08.dbf'),
str(CENSO2010 / 'Personas_09.dbf'),
str(CENSO2010 / 'Personas_10.dbf'),
str(CENSO2010 / 'Personas_11.dbf'),
str(CENSO2010 / 'Personas_12.dbf'),
str(CENSO2010 / 'Personas_13.dbf'),
str(CENSO2010 / 'Personas_14.dbf'),
str(CENSO2010 / 'personas_15.dbf'),
str(CENSO2010 / 'Personas_16.dbf'),
str(CENSO2010 / 'Personas_17.dbf'),
str(CENSO2010 / 'Personas_18.dbf'),
str(CENSO2010 / 'Personas_19.dbf'),
str(CENSO2010 / 'Personas_20.dbf'),
str(CENSO2010 / 'Personas_21.dbf'),
str(CENSO2010 / 'Personas_22.dbf'),
str(CENSO2010 / 'Personas_23.dbf'),
str(CENSO2010 / 'Personas_24.dbf'),
str(CENSO2010 / 'Personas_25.dbf'),
str(CENSO2010 / 'Personas_26.dbf'),
str(CENSO2010 / 'Personas_27.dbf'),
str(CENSO2010 / 'Personas_28.dbf'),
str(CENSO2010 / 'Personas_29.dbf'),
str(CENSO2010 / 'Personas_30.dbf'),
str(CENSO2010 / 'Personas_31.dbf'),
str(CENSO2010 / 'Personas_32.dbf')]

##We first drag the info of the ppl survey  THIS FUCKING SHUT IS ENCODED DIFFERENTLY

import geopandas as gpd 
def df2010_create(y):
    db=pd.DataFrame() 
    for x in y :
        temp = gpd.read_file(x)
        temp = pd.DataFrame(temp)
        db = pd.concat([db, temp], axis=0)
    for i in list(db.columns):
            try:
                db[i] = db[i].astype(int)
            except:
                pass
    return(db)

df2010ppl = df2010_create( paths_ppl)

columns = df2010ppl.columns.tolist()
for i in columns:
    df2010ppl[i] = pd.to_numeric(df2010ppl[i], errors='coerce', downcast='integer')
    
df2010ppl.to_csv(str(CENSO2010 / 'census_people2010.csv'), index = True)

pathppl = str(CENSO2010 / 'census_people2010.csv')
df2010ppl= pd.read_csv(pathppl)

school2010 = df2010ppl.loc[df2010ppl['EDAD'].isin([  15, 16, 17]), 
            ['ENT', 'MUN', 'FACTOR','SEXO', 'EDAD', 'ASISTEN', 'ESCOACUM']]

school2010 = school2010.reset_index()


df2010ppl.loc[df2010ppl['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
school2010.loc[school2010['ASISTEN'].isin([3, 9]), 'ASISTEN']= 0
school2010 = school2010.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ENROLL_RATE': (x['ASISTEN'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()

df2010ppl = df2010ppl.loc[df2010ppl['EDAD']>=18, ['ENT', 'MUN', 'FACTOR','ESCOACUM']]   
df2010ppl = df2010ppl.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ESCOACUM': (x['ESCOACUM'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()
school2010 = school2010.merge(df2010ppl, on=(['ENT', 'MUN']), how= 'left')

school2010['YEAR'] = 2010

school2010 = school2010.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
school2010 = school2010[['ENT', 'MUN', 'CVEGEO', 'YEAR','ENROLL_RATE', 'ESCOACUM' ]]
school2010.to_csv(str(CENSO2010 / 'school10.csv'), index = True)
del school2010,  df2010ppl

##For 2020
path_c2020_personas= str(CENSO2020 / 'Personas00.CSV')

df2020ppl=pd.read_csv(path_c2020_personas)

school2020 = df2020ppl.loc[df2020ppl['EDAD'].isin([  15, 16, 17]), 
                           ['ENT', 'MUN', 'FACTOR','SEXO', 'EDAD', 'ASISTEN', 'ESCOACUM']]

df2020ppl.loc[df2020ppl['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
school2020.loc[school2020['ASISTEN'].isin([3, 9]), 'ASISTEN']= 0
school2020 = school2020.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ENROLL_RATE': (x['ASISTEN'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()

df2020ppl = df2020ppl.loc[df2020ppl['EDAD']>=18, ['ENT', 'MUN', 'FACTOR','ESCOACUM']]   
df2020ppl = df2020ppl.groupby(['ENT', 'MUN']).apply(lambda x: pd.Series({
       'ESCOACUM': (x['ESCOACUM'] * x['FACTOR']).sum() / x['FACTOR'].sum()})).reset_index()
school2020 = school2020.merge(df2020ppl, on=(['ENT', 'MUN']), how= 'left')

school2020['YEAR'] = 2020

school2020 = school2020.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
school2020 = school2020[['ENT', 'MUN', 'CVEGEO', 'YEAR','ENROLL_RATE', 'ESCOACUM' ]]
school2020.to_csv(str(CENSO2020 / 'school20.csv'), index = True)
del school2020,  df2020ppl


###### And population as a control 

municipalities = str(CENSO2020 / 'Municipalities info.csv')
mex_info= pd.read_csv(municipalities)

#for1990
#pop1990path= [str(CENSO1990 / 'iter_naldbf90.dbf')]
#pop1990 = df2010_create( pop1990path)

#pop1990.to_csv(str(CENSO1990 / 'POP_CORE90.csv'), index = True)

pop1990 = str(CENSO1990 / 'POP_CORE90.csv')
pop1990= pd.read_csv(pop1990)
##altitude is full of none 
pop1990.rename(columns = {'ENTIDAD':'ENT' , 'P_TOTAL':'POBTOT' , 'P_E_ACT':'PEA'   }, inplace = True)
pop1990 = pop1990.loc[pop1990['LOC'] == 0, 
            ['ENT', 'MUN', 'POBTOT','PEA', 'POB_OCUP']]
for i in ['PEA', 'POB_OCUP']:
    pop1990[i] =pd.to_numeric(pop1990[i], errors='coerce')
    
pop1990['PDESOCUP'] = pop1990['PEA']  - pop1990['POB_OCUP'] 
pop1990 = pop1990.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'right')
pop1990['YEAR'] = 1990
pop1990 = pop1990[['ENT', 'MUN', 'CVEGEO', 'YEAR', 'POBTOT','PEA', 'PDESOCUP' ]]

pop1990.to_csv(str(CENSO1990 / 'pop90.csv'), index = True)

del pop1990,  i

#For 2000

#pop2000 = [str(CENSO2000 / 'ITER_NALDBF00.dbf')]
#pop2000= df2010_create(pop2000)
#pop2000.to_csv(str(CENSO2000 / 'pop_core00.csv'), index = True)

pop2000 = str(CENSO2000 / 'pop_core00.csv')
pop2000= pd.read_csv(pop2000)

for i in ['POBTOT', 'PSDERSS' , 'PECOACTIV', 'POCUPADA' , 'ALTITUD' ]:
    pop2000[i] =pd.to_numeric(pop2000[i], errors='coerce')
    
pop2000.rename(columns = {'ENTIDAD':'ENT' , 'PSDERSS':'PSINDER' , 'PECOACTIV':'PEA'   }, inplace = True)

temp =  pop2000.groupby(['ENT', 'MUN'])['ALTITUD'].mean()    

pop2000 = pop2000.loc[pop2000['LOC'] == 0, 
            ['ENT', 'MUN', 'POBTOT','PEA', 'POCUPADA', 'PSINDER']]
pop2000 = pop2000.merge(temp, on=(['ENT', 'MUN']), how= 'left')
pop2000['PDESOCUP'] = pop2000['PEA']  - pop2000['POCUPADA'] 

pop2000 = pop2000.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'right')
pop2000['YEAR'] = 2000
pop2000 = pop2000[['ENT', 'MUN', 'CVEGEO', 'YEAR', 'ALTITUD' ,'POBTOT','PEA', 'PDESOCUP' ]]
pop2000.to_csv(str(CENSO2000 / 'pop00.csv'), index = True)
del pop2000, temp, i



#For 2010
pop2010path=[ str(CENSO2010 / 'ITER_NALDBF10.dbf')]


pop2010 = df2010_create( pop2010path)
pop2010.to_csv(str(CENSO2010 / 'pop10.csv'), index = True)
pop2010['ALTITUD'] =pd.to_numeric(pop2010['ALTITUD'], errors='coerce')
temp =  pop2010.groupby(['ENTIDAD', 'MUN'])['ALTITUD'].mean()

pop2010 = pop2010.loc[pop2010['LOC'] == 0, 
            ['ENTIDAD', 'MUN', 'POBTOT','PEA', 'PDESOCUP', 'PSINDER']]
pop2010 = pop2010.merge(temp, on=(['ENTIDAD', 'MUN']), how= 'left')

pop2010 = pop2010.merge(mex_info, left_on=(['ENTIDAD', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'right')
pop2010.rename(columns = {'ENTIDAD':'ENT'}, inplace = True)
pop2010['YEAR'] = 2010
pop2010 = pop2010[['ENT', 'MUN', 'CVEGEO', 'YEAR','ALTITUD', 'POBTOT','PEA', 'PDESOCUP', 'PSINDER' ]]
pop2010.to_csv(str(CENSO2010 / 'pop10.csv'), index = True)
del pop2010, pop2010path, temp

#For 2020

pop2020 = str(CENSO2020 / 'ITER_NALCSV20.csv')
pop2020= pd.read_csv(pop2020)

for i in ['POBTOT', 'PSINDER' , 'PEA', 'PDESOCUP' , 'ALTITUD' ]:
    pop2020[i] =pd.to_numeric(pop2020[i], errors='coerce')
    
pop2020.rename(columns = {'ENTIDAD':'ENT'  }, inplace = True)

temp =  pop2020.groupby(['ENT', 'MUN'])['ALTITUD'].mean()    

pop2020 = pop2020.loc[pop2020['LOC'] == 0, 
            ['ENT', 'MUN', 'POBTOT','PEA', 'PDESOCUP', 'PSINDER']]
pop2020 = pop2020.merge(temp, on=(['ENT', 'MUN']), how= 'left')

pop2020 = pop2020.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'right')
pop2020['YEAR'] = 2020
pop2020 = pop2020[['ENT', 'MUN', 'CVEGEO', 'YEAR', 'ALTITUD' ,'POBTOT','PEA', 'PDESOCUP' ]]
pop2020.to_csv(str(CENSO2020 / 'pop20.csv'), index = True)
del pop2020, temp, i