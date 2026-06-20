# -*- coding: utf-8 -*-

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from config import ROOT, CENSO1990, CENSO2000, CENSO2010, CENSO2020, CORE, NDVI_DIR, LANDUSE, RESULTS

import pandas as pd
import numpy as np
import pyreadstat
from sklearn.preprocessing import StandardScaler



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

fiscal = fiscal[['Department', 'Municipality','Income2020',]]
mex_info = mex_info.merge(fiscal, how= 'left', left_on= ['CVE_ENT', 'NOMGEO'], right_on= [ 'Department', 'Municipality'])
mex_info.drop(['Department', 'Municipality'], inplace=True, axis=1)
# the amount of NA in fiscal revenue is 9% (225)   mex_info['Income2020'].isna().sum()  / 2469


del land, land2, fiscal, fiscal_path


mines_match_path= str(CENSO2020 / 'mines_neighbors.csv')
minex_path= str(CENSO2020 / 'Minex_data.csv')


minex = pd.read_csv(minex_path)
df = pd.read_csv(mines_match_path)

##We keep mexico only

minex = minex[minex.Country == 'Mexico']

##We construct dummies for the info need it 
minex.rename(columns = {'Contained':'Contained Commodities', 'Current St':'Current Status', 
                        'Primary Me':'Primary Metal'}, inplace = True)
clean_minex =pd.DataFrame( minex[['ID No', 'Contained Commodities', 'Current Status']]) ##'Contained Commodities', 'Current Status'
variable = ['Primary Metal', 'Size' ]
for x in variable :
    data_dummies = pd.get_dummies(minex[x],prefix=x)
    clean_minex = pd.concat([clean_minex, data_dummies], axis=1)
    del data_dummies

##Also for the minerals extracted in a given mine    
unique_commodities= ['Cu', 'Au', 'C_graphite', 'Fe', 'Li', 'Mn', 'Mo', 'Ag', 'W', 'Zn', 'Calc', 
                     'K', 'Pb', 'REE', 'Sb', 'Ay', 'Clays']

for i in unique_commodities:
    clean_minex[i] = clean_minex.apply(lambda row: float(i in row['Contained Commodities'])  , axis=1 )

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
  
clean_minex['Operating'] = clean_minex.apply(lambda row: float(row['Current Status'] in Operating )  , axis=1 )
clean_minex['Exploration'] = clean_minex.apply(lambda row: float(row['Current Status'] in Exploration )  , axis=1 )
clean_minex['Feasibility'] = clean_minex.apply(lambda row: float(row['Current Status'] in Feasibility )  , axis=1 )
clean_minex['Closed'] = clean_minex.apply(lambda row: float(row['Current Status'] in Closed )  , axis=1 )
clean_minex['Stalled'] = clean_minex.apply(lambda row: float(row['Current Status'] in Stalled )  , axis=1 )
clean_minex['Other_status'] = clean_minex.apply(lambda row: float(row['Current Status'] in Other_status )  , axis=1 )

## Generating FE for year of discovery and year that start operating 

data_dummies = pd.get_dummies(minex['Discovery'],prefix='Discovery' , prefix_sep='_')
data_dummies['Discovery_older80s'] = minex.apply(lambda row: float(row['Discovery'] <1980 )  , axis=1 ) 
to_delete = ['Discovery_1950', 'Discovery_1951', 'Discovery_1953', 'Discovery_1955',
        'Discovery_1957', 'Discovery_1958', 'Discovery_1959', 'Discovery_1960',
        'Discovery_1963', 'Discovery_1964', 'Discovery_1967', 'Discovery_1968',
        'Discovery_1970', 'Discovery_1971', 'Discovery_1972', 'Discovery_1973',
        'Discovery_1974', 'Discovery_1975', 'Discovery_1976', 'Discovery_1977',
        'Discovery_1979' ] 
for i in to_delete:
    try:
        data_dummies.drop([i], axis=1, inplace=True)
    except:
        pass
clean_minex = pd.concat([clean_minex, data_dummies], axis=1)

def algo(x) :
    if type(x) == str :
         z= min(map(int , x.split(',')))
         
    if type(x)== float :
        z= float(x)
    return(z)
        
minex['Start_year'] = minex.apply(lambda row: algo(row['Mine Start'])  , axis=1 )

data_dummies = pd.get_dummies(minex['Start_year'],prefix='Start' , prefix_sep='_')
data_dummies['Start_older80s'] = minex.apply(lambda row: float(row['Start_year'] <1980 )  , axis=1 ) 
        
to_delete = ['Start_1952.0', 'Start_1953.0', 'Start_1954.0', 'Start_1960.0',
       'Start_1961.0', 'Start_1967.0', 'Start_1968.0', 'Start_1971.0',
       'Start_1973.0', 'Start_1974.0', 'Start_1976.0' ] 

for i in to_delete:
    try:
        data_dummies.drop([i], axis=1, inplace=True)
    except:
        pass


clean_minex = pd.concat([clean_minex, data_dummies], axis=1)

##Clean a lil the memory
del Operating, Exploration, Feasibility, Closed, Stalled, Other_status, i, x,   variable, minex



#################### Merging with data on municipalities ####################
## Because I need to collapse the data at municipality lvl, and I have 3 types of neighbors (25, 50, 75km), then 
## Im gonna collapse the info 3 times each for a set of neighbors

df.columns = ['CVEGEO', 'CVE_ENT',  'CVE_MUN',  'NOMGEO',  '25km',  '50km',  '75km']

def buffer_info(data, size):
    df2 = data.groupby(by=["CVEGEO", size]).max()
    df2= df2.reset_index()
    df2 = df2[["CVEGEO", size]]
    df2 = df2.merge(right=clean_minex ,left_on=size , right_on='ID No', how='left', suffixes = ('', size) )
    df2= df2.groupby(by=["CVEGEO"]).max()
    df2.drop([size, 'ID No', 'Contained Commodities', 'Current Status'], axis=1, inplace=True)
    df2= df2.add_suffix(size)
    return df2

km25=buffer_info(df, '25km')
km50 = buffer_info(df, '50km')
km75=buffer_info(df, '75km')


for i in [km25, km50, km75]:
    mex_info= mex_info.merge(right=i, on='CVEGEO', how = 'outer' )

del km25, km50, km75, clean_minex

mex_info = mex_info.fillna(0)


############## Dealing with the weight matrix  ####################
#neigh= str(CENSO2020 / 'Municipalities neighbors.csv')
#neigh = pd.read_csv(neigh)

#neigh = neigh[['CVEGEO' , 'Neighbors']]

#for i in neigh['CVEGEO'] :
#    neigh[str(i)] = neigh.apply(lambda row: float( str(i) in row['Neighbors'])  , axis=1 )
    
#neigh = neigh.set_index('CVEGEO')   
#neigh.drop(['Neighbors'], axis=1, inplace=True)

#neigh.to_csv(str(CENSO2020 / 'weight_matrix.csv'), index = True)

#del data_dummies, df, i, neigh, to_delete


## Adding the data 
income_path=str(ROOT / 'conjunto_de_datos_enigh2016_nueva_serie_csv/conjunto_de_datos_ingresos_enigh_2016_ns/conjunto_de_datos/conjunto_de_datos_ingresos_enigh_2016_ns.csv')
#The data of the household survey is aggregated at department  level,hence it does not work for us

## Path of the census data 
path_c2020_viviendas= str(CENSO2020 / 'Viviendas00.CSV')
path_c2020_personas= str(CENSO2020 / 'Personas00.CSV')

df=pd.read_csv(path_c2020_viviendas)


#Income has null values 
#I have to match info of the head of the family


df.loc[df['INGTRHOG'].isin([999999]),'INGTRHOG']=np.nan  #Income is hard capped
df.loc[df['JEFE_SEXO'].isin([3]),'JEFE_SEXO']=0 #mujer es 3
df.loc[df['JEFE_EDAD'].isin([999]),'JEFE_EDAD']=np.nan


#data from the ppl, slicing only the head of the family and the variables that i need: 
    #years of schooling, Indigeneaus languages, Afro
temp = pd.read_csv(path_c2020_personas)
temp = temp.loc[(temp['PARENTESCO']==101), ['ID_VIV', 'ESCOACUM', 'HLENGUA', 'AFRODES']] 

to_dummy = ['HLENGUA', 'AFRODES']

for var in to_dummy:
    temp.loc[temp[var].isin([3, 9]),var]=0
    
temp.loc[temp['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 
    
df= df.merge(temp, on='ID_VIV', how= 'inner')
del temp

##To make wealth index
# 1. make the variables to use as each variable encode different types that do not mean a better situation per se, eg. floor in cement or in wood
# 2. normalize 
# 3. PCA

##print(df.columns) to see the names of the columns
## df['ENT'].value_counts() To see frequency of a column
## pd.get_dummies to make dummies for each option
## df['INGTRHOG'].isna().sum() to count nan 
##algo.describe().apply(lambda s: s.apply('{0:.5f}'.format))


### Cleaning the data 
algo=pd.DataFrame(data=df['ID_VIV'])

def dummies(var, yes, no):
    if type(yes)==list:
        algo.loc[df[var].isin(yes),var]=1
    else:
        algo.loc[df[var].isin([yes]),var]=1
    if type(no)==list:
        algo.loc[df[var].isin(no),var]=0
    else:
        algo.loc[df[var].isin([no]),var]=0
    algo[var].fillna(inplace=True, value=0)
    
dummies('COCINA', 1,3) 
dummies('ESTUFA', 1,3) 
dummies('ELECTRICIDAD', 1,3)     
dummies('TINACO', 1,2)   
dummies('CISTERNA', 3, 4)   
dummies('BOMBA_AGUA', 5,6) 
dummies('REGADERA', 7,8) 
dummies('BOILER', 1,2) 
dummies('CALENTADOR_SOLAR', 3,4) 
dummies('AIRE_ACON', 5,6) 
dummies('PANEL_SOLAR', 7,8) 
dummies('USOEXC', 1,3) 
dummies('REFRIGERADOR', 1,2) 
dummies('LAVADORA', 3,4) 
dummies('HORNO', 5,6) 
dummies('AUTOPROP', 7,8) 
dummies('MOTOCICLETA', 1,2) 
dummies('BICICLETA', 3,4) 
dummies('RADIO', 5,6) 
dummies('TELEVISOR', 7,8) 
dummies('COMPUTADORA', 1,2) 
dummies('TELEFONO', 3,4) 
dummies('CELULAR', 5,6) 
dummies('INTERNET', 7,8) 
dummies('SERV_TV_PAGA', 1,2) 
dummies('SERV_PEL_PAGA', 3,4) 
dummies('CON_VJUEGOS', 5,6) 
dummies('AGUA_ENTUBADA', [1],[3,9])
dummies('CLAVIVP', [1, 2, 3, 4, 5],[6, 7, 8, 9])
dummies('PAREDES', [8] , [1, 2, 3, 4, 5, 6, 7])
dummies('TECHOS', [4, 5, 9, 10], [1, 2, 3, 6, 7, 8])
dummies('PISOS', [2, 3], 1 )
dummies('COMBUSTIBLE', [2, 3],[1, 4, 5])
dummies('ABA_AGUA_ENTU', [1],[2, 3, 4, 5, 6, 7])
dummies('SERSAN', [1],[2, 3])
dummies('DRENAJE', [1, 2],[3, 4, 5, 9])

def countin(var, no_especificado):
    algo[var]=df[var]
    algo.loc[df[var].isin([no_especificado]),var]=0
    df[var].fillna(inplace=True, value=0)
    
countin('CUADORM', 99)
countin('TOTCUART', 99)
countin('FOCOS', 999)
countin('FOCOS_AHORRA', 999)




############# Making variables ###########
#variables excluded 'LUG_COC', 'ABA_AGUA_ENTU', 'ABA_AGUA_NO_ENTU', 'CONAGUA', 'DESTINO_BAS', 'FORMA_ADQUI'
variable = ['TENENCIA', 'ESCRITURAS' ]

for x in variable :
    data_dummies = pd.get_dummies(df[x],prefix=x)
    algo = pd.concat([algo, data_dummies], axis=1)

algo = algo.set_index('ID_VIV')
del data_dummies

## We have problems with NA, and droping variables, hence i try to reduce the number of variables to use
## The reference uses 24 and i have over 100 
## ademas muy pocas variables presentan alta correlacion     algo.corr()

##We drop all variables that have over 95% concentration: electridad, paneles, clase de vivienda
to_delete = ['ELECTRICIDAD', 'PANEL_SOLAR', 'CLAVIVP', 
     'FOCOS', 'CLAVIVP_8', 'CLAVIVP_9', 'CLAVIVP_99', 'PAREDES_1.0', 'PAREDES_2.0','PAREDES_9.0', 
            'TECHOS_1.0', 'TECHOS_2.0', 'TECHOS_99.0', 'PISOS_1.0', 'PISOS_9.0',  'COMBUSTIBLE_1.0', 'COMBUSTIBLE_4.0', 
'COMBUSTIBLE_5.0', 'COMBUSTIBLE_9.0', 'SERSAN_3.0',  'SERSAN_9.0', 'DRENAJE_9.0', 'TENENCIA_9.0', 'ESCRITURAS_8.0', 'ESCRITURAS_9.0' ]
for i in to_delete:
    try:
        algo.drop([i], axis=1, inplace=True)
    except:
        pass

####### 2. normalize ###########
columns = algo.columns.tolist()

algo=StandardScaler().fit_transform(algo)
algo = pd.DataFrame(data= algo, index = df['ID_VIV'], columns= columns)
df = df.set_index('ID_VIV')

#Putting variables that do not need to be normalize
to_put = ['INGTRHOG', 'ESCOACUM', 'HLENGUA', 'AFRODES', 'JEFE_SEXO', 'JEFE_EDAD', 'NUMPERS', 'FACTOR', 'ENT', 'MUN'  ]
for i in to_put:
    algo[i]=df[[i]]


algo = algo.merge(mex_info, left_on=(['ENT', 'MUN']), right_on=(['CVE_ENT' , 'CVE_MUN']), how= 'left')
algo["year"] = 2020

###### Because data has weights and missing values i cannot use the PCA of python...
algo.to_csv(str(CENSO2020 / 'data_mexico.csv'), index = True)

##To generate a sample bd
#sample = pd.concat([algo.head(50), algo.tail(50)])
#sample.to_csv(str(CENSO2020 / 'sample.csv'), index = True)
##pca_house = PCA(n_components=1)
##PCA_house = pca_house.fit_transform(algo)


##People
paths =[str(CENSO2010 / "personas_01.dta")),
str(CENSO2010 / "personas_02.dta")),
str(CENSO2010 / "personas_03.dta")),
str(CENSO2010 / "personas_04.dta")),
str(CENSO2010 / "personas_05.dta")),
str(CENSO2010 / "personas_06.dta")),
str(CENSO2010 / "personas_07.dta")),
str(CENSO2010 / "personas_08.dta")),
str(CENSO2010 / "personas_09.dta")),
str(CENSO2010 / "personas_10.dta")),
str(CENSO2010 / "personas_11.dta")),
str(CENSO2010 / "personas_12.dta")),
str(CENSO2010 / "personas_13.dta")),
str(CENSO2010 / "personas_14.dta")),
str(CENSO2010 / "personas_15.dta")),
str(CENSO2010 / "personas_16.dta")),
str(CENSO2010 / "personas_17.dta")),
str(CENSO2010 / "personas_18.dta")),
str(CENSO2010 / "personas_19.dta")),
str(CENSO2010 / "personas_20.dta")),
str(CENSO2010 / "personas_21.dta")),
str(CENSO2010 / "personas_22.dta")),
str(CENSO2010 / "personas_23.dta")),
str(CENSO2010 / "personas_24.dta")),
str(CENSO2010 / "personas_25.dta")),
str(CENSO2010 / "personas_26.dta")),
str(CENSO2010 / "personas_27.dta")),
str(CENSO2010 / "personas_28.dta")),
str(CENSO2010 / "personas_29.dta")),
str(CENSO2010 / "personas_30.dta")),
str(CENSO2010 / "personas_31.dta")),
str(CENSO2010 / "personas_32.dta"))]


y = pd.DataFrame() 

for algo in paths:
    df , meta= pyreadstat.read_dta(algo)
    temp = df.loc[(df['parent']==1), ['id_viv', 'escoacum', 'hlengua', 'sexo' ,'edad' ]] ##Afro is not in the survey
    y = pd.concat([y, temp], axis=0)
    del temp, df

y.columns = [name.upper() for name in list(y.columns)]

y.loc[y['HLENGUA'].isin([3, 9]), 'HLENGUA']=0
    
y.loc[y['ESCOACUM'].isin([99]), 'ESCOACUM']= np.nan 

y.loc[y['SEXO'].isin([3]),'SEXO']=0

y.loc[y['EDAD'].isin([999]),'EDAD']=np.nan 

y.to_csv(str(CENSO2010 / 'personas2010.csv'), index = True)  

##households
paths =[
str(CENSO2010 / "viviendas_01.dta"),
str(CENSO2010 / "viviendas_02.dta"),
str(CENSO2010 / "viviendas_03.dta"),
str(CENSO2010 / "viviendas_04.dta"),
str(CENSO2010 / "viviendas_05.dta"),
str(CENSO2010 / "viviendas_06.dta"),
str(CENSO2010 / "viviendas_07.dta"),
str(CENSO2010 / "viviendas_08.dta"),
str(CENSO2010 / "viviendas_09.dta"),
str(CENSO2010 / "viviendas_10.dta"),
str(CENSO2010 / "viviendas_11.dta"),
str(CENSO2010 / "viviendas_12.dta"),
str(CENSO2010 / "viviendas_13.dta"),
str(CENSO2010 / "viviendas_14.dta"),
str(CENSO2010 / "viviendas_15.dta"),
str(CENSO2010 / "viviendas_16.dta"),
str(CENSO2010 / "viviendas_17.dta"),
str(CENSO2010 / "viviendas_18.dta"),
str(CENSO2010 / "viviendas_19.dta"),
str(CENSO2010 / "viviendas_20.dta"),
str(CENSO2010 / "viviendas_21.dta"),
str(CENSO2010 / "viviendas_22.dta"),
str(CENSO2010 / "viviendas_23.dta"),
str(CENSO2010 / "viviendas_24.dta"),
str(CENSO2010 / "viviendas_25.dta"),
str(CENSO2010 / "viviendas_26.dta"),
str(CENSO2010 / "viviendas_27.dta"),
str(CENSO2010 / "viviendas_28.dta"),
str(CENSO2010 / "viviendas_29.dta"),
str(CENSO2010 / "viviendas_30.dta"),
str(CENSO2010 / "viviendas_31.dta"),
str(CENSO2010 / "viviendas_32.dta")]

df= pd.DataFrame()

for algo in paths:
    temp , meta= pyreadstat.read_dta(algo)
    df = pd.concat([df, temp], axis=0)
    del temp

df.columns = [name.upper() for name in list(df.columns)]
df= df.merge(y, on='ID_VIV', how= 'inner')
del y

df.loc[df['INGTRHOG'].isin([999999]),'INGTRHOG']=np.nan  #Income is hard capped
### Cleaning the data 
algo=pd.DataFrame(data=df['ID_VIV'])

def dummies(var, yes, no):
    if type(yes)==list:
        algo.loc[df[var].isin(yes),var]=1
    else:
        algo.loc[df[var].isin([yes]),var]=1
    if type(no)==list:
        algo.loc[df[var].isin(no),var]=0
    else:
        algo.loc[df[var].isin([no]),var]=0
    algo[var].fillna(inplace=True, value=0)
    
dummies('COCINA', 1,3) 
dummies('ELECTRI', 1,[3,9])     
dummies('ESTUFAG', 1,[2,9])  
dummies('TINACO', 1,[2,9])   
dummies('CISTERNA', 1, [2,9])   
dummies('BOILER', 3,[4,9]) 
dummies('REGADERA', 3,[4,9]) 
dummies('MEDLUZ', 1,[2,9]) 
dummies('RADIO', 1,[2,9])
dummies('TELEVI', 3,[4,9]) 
dummies('REFRIG', 1,[2,9])
dummies('LAVADORA', 3,[4,9]) 
dummies('AUTOPROP', 1,[2,9])
dummies('COMPU', 3,[4,9]) 
dummies('CLAVIVP', [1, 2, 3],[ 4, 5, 6, 7, 9])
dummies('PAREDES', [8], [1, 2, 3, 4, 5, 6, 7, 9])
dummies('TECHOS', [4, 8, 9], [1, 2, 3, 5, 6, 7, 99])
dummies('PISOS', [2, 3],[1,9] )


def countin(var, no_especificado):
    algo[var]=df[var]
    algo.loc[df[var].isin([no_especificado]),var]=0
    df[var].fillna(inplace=True, value=0)
    
countin('CUADORM', 99)
countin('TOTCUART', 99)

####### 2. normalize ###########
columns = algo.columns.tolist()

algo=StandardScaler().fit_transform(algo)
algo = pd.DataFrame(data= algo, index = df['ID_VIV'], columns= columns)
df = df.set_index('ID_VIV')

#Putting variables that do not need to be normalize
to_put = ['INGTRHOG', 'ESCOACUM', 'HLENGUA', 'SEXO', 'EDAD', 'NUMPERS', 'FACTOR', 'ENT', 'MUN'  ]
for i in to_put:
    algo[i]=df[[i]]
    
algo["year"] = 2010    
 

algo.to_csv(str(CENSO2010 / 'viviendas2010.csv'), index = True)  


