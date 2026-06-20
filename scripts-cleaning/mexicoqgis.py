from pathlib import Path as _Path
ROOT = _Path(r"C:/Users/Jos3/Documents/Mexico")  # update to your clone path

for i in [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]:
    processing.run("native:buffer", {'INPUT':str(CENSO2020 / 'Minex_Mexico.shp'),'DISTANCE':int(i*1000),'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':str(CENSO2020 / 'Maps_data' / ('buffer_'+str(i)+'.shp'))})


for i in [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]:
    processing.run("native:intersection", {'INPUT':str(CENSO2020 / 'Mexico_Map.shp')+'|layername=Mexico_Map','OVERLAY':str(CENSO2020 / 'Maps_data' / ('buffer_'+str(i)+'.shp')),'INPUT_FIELDS':['CVEGEO','CVE_ENT','CVE_MUN'],'OVERLAY_FIELDS':['ID No'],'OUTPUT':str(CENSO2020 / 'Maps_data' / ('Intersection_'+str(i)+'.shp'))})
 
for i in [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]: 
    processing.run("native:exporttospreadsheet", {'LAYERS':[str(CENSO2020 / 'Maps_data' / ('Intersection_'+str(i)+'.shp'))],'USE_ALIAS':False,'FORMATTED_VALUES':False,'OUTPUT':str(CENSO2020 / 'Maps_data' / ('Intersection_'+str(i)+'.xlsx')),'OVERWRITE':True})
    
    
    
    processing.run("gdal:translate", {'INPUT':'HDF4_EOS:EOS_GRID:'+str(ROOT / 'NDVI' / 'January' / 'MOD13Q1.A2003017.h07v05.061.2020090100006.hdf')+':MODIS_Grid_16DAY_250m_500m_VI:"250m 16 days NDVI"','TARGET_CRS':None,'NODATA':None,'COPY_SUBDATASETS':False,'OPTIONS':'','EXTRA':'','DATA_TYPE':0,'OUTPUT':str(ROOT / 'NDVI' / 'January' / 'algo.tif')})