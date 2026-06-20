# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:33:50 2023

CLEANIN MINEX  AND THE OTHER MUNICIPALITY LEVEL VAR

@author: Jos3
"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from config import ROOT, CENSO1990, CENSO2000, CENSO2010, CENSO2020, CORE, NDVI_DIR, LANDUSE, RESULTS

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
#   For a graph of descriptive statistics
#
#######################################################


######################################################
#
#   For different tests on particular types of mines
#
#######################################################




#########################################
# FOR QUALITY OF WATER BASED ON RING FROM THE MINE
#
#############################################

#########################################
# FOR QUALITY OF AIR BASED ON RING FROM THE MINE
#
#############################################

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
   mona = mona.groupby('CVEGEO').agg(agg_func) #if we use agg_func2 it takes into account controls
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




###
# Dealing with rings --> lets see how this go
###
#path = str(ROOT / '"mapa"' / 'ring25to50.xlsx')

del agg_func['CVE_ENT'] , agg_func['CVE_MUN']
for x in [ 25, 50]:
    y = 0
    if x==20 :
        y = x+20
    else:
        y=x+25
    luna = pd.read_excel(str(ROOT / '"mapa"' / 'ring')+str(x)+'to'+str(y)+'.xlsx')
    luna['Prc_cover'] = luna['area_2']/luna['area']
    ## We drop those municipalities where less than 50% is cover by the ring 
    luna = luna[luna['Prc_cover']>=0.5]
    luna = luna.merge(right = minex, how = 'left', on = 'ID No')
    luna = luna.sort_values('CVEGEO')

    luna = luna.groupby('CVEGEO').agg(agg_func)
    luna.rename(columns = {'ID No':'No_mines'}, inplace=(True))
    luna.to_csv(str(CORE / ('ring'+str(x)+'.csv')), index = True)
    del luna


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