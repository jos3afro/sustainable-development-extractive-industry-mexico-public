from pathlib import Path as _Path
ROOT = _Path(r"C:/Users/Jos3/Documents/Mexico")  # update to your clone path


##to deal with laND USE

#Find out which band is the correct --> it's band 14
import os
import glob  # For finding files with patterns
from qgis.core import QgsVectorLayer, QgsRasterLayer

# Save each band for each year available 
# Base directory where HDF files are stored
base_dir = str(LANDUSE) + "/"

existing_files = os.listdir(base_dir)
# Loop through the years of interest
for year in range(2001, 2021):
    
    output_path2 = str(LANDUSE / f'UrbanArea_{year}.xlsx')
    if output_path2 in existing_files :
        print(f'Ok for {year}')
    else:
        # Search for the file matching the pattern for the specific year
        pattern = f"MCD12C1.A{year}001.*.hdf"
        matching_files = glob.glob(os.path.join(base_dir, pattern))
        
        if len(matching_files) == 0:
            print(f"No file found for year {year}. Skipping...")
            continue  # Skip to the next year if no file matches
        
        if len(matching_files) > 1:
            print(f"Multiple files found for year {year}. Using the first one...")
        
        # Use the first matching file
        input_file = matching_files[0]
        output_path = f'{base_dir}/UrbanArea_{year}.tif'

        
        hdf_file_path = f'HDF4_EOS:EOS_GRID:"{input_file}":MOD12C1:Land_Cover_Type_1_Percent'        
        hdf_layer = QgsRasterLayer(hdf_file_path, input_file)
        QgsProject.instance().addMapLayer(hdf_layer)
        
        # Run the processing algorithm
        processing.run("gdal:rearrange_bands", {
            'INPUT': hdf_file_path,  # Use the dynamically fetched file
            'BANDS': [14],  # Specify the desired band
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'OUTPUT': output_path  # Use the formatted output path
        })
        print(f"Processed year {year} and saved to {output_path}")


    # Run statistics of urban area! (to run reg on rural area 
         
        processing.run("native:zonalstatisticsfb", {
            'INPUT':str(ROOT / '"mapa"' / 'conjunto_de_datos/00mun.shp'),
            'INPUT_RASTER': output_path,
            'RASTER_BAND':1,
            'COLUMN_PREFIX':'_','STATISTICS':[1,2,3],
            'OUTPUT': output_path2 })
        
        QgsProject.instance().removeMapLayer(hdf_layer)

#Find out how to automate calculator and get a 0, 1 layout
# Input and output paths

# Paths
path_rasters = str(LANDUSE) + "/"
path_vector = str(CENSO2020 / 'Mexico_Map.shp')

for year in range(2001, 2021):
    try:
        input_raster = f"{path_rasters}UrbanArea_{year}.tif"
        output_raster = f"{path_rasters}Dichotomized_UrbanArea_{year}.tif"
        output_vector = f"{path_rasters}vectorized_{year}.shp"
        output_mex = f"{path_rasters}mexico_noUrban_{year}.shp"
        
        print(f"Processing year {year}...")
        
        # Dichotomize the raster
        processing.run("gdal:rastercalculator", {
            'INPUT_A': input_raster,
            'BAND_A': 1,
            'FORMULA': 'A>=1',
            'NO_DATA': None,
            'RTYPE': 5,  # Byte output for binary raster
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': output_raster
        })
        print(f"Dichotomized raster saved to {output_raster}")
        
        # Vectorize the raster
        processing.run("gdal:polygonize", {
            'INPUT': output_raster,
            'BAND': 1,
            'FIELD': 'DN',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': output_vector
        })
        print(f"Vectorized raster saved to {output_vector}")
        
        # Perform intersection
        processing.run("native:intersection", {
            'INPUT': output_vector,
            'OVERLAY': f"{path_vector}|layername=Mexico_Map",
            'INPUT_FIELDS': [],
            'OVERLAY_FIELDS': ['CVEGEO'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': output_mex
        })
        print(f"Intersection saved to {output_mex}")
        
        print(f"Done with {year}\n")
    except Exception as e:
        print(f"Error processing year {year}: {e}")

#Keep only zeros

for year in range(2001, 2021):
    try:
        input_shapefile = f"{path_rasters}mexico_noUrban_{year}.shp"
        filtered_output = f"{path_rasters}filtered_noUrban_{year}.shp"
        
        print(f"Filtering polygons where DN == 0 for year {year}...")

        # Filter polygons where DN == 0
        processing.run("native:extractbyattribute", {
            'INPUT': input_shapefile,
            'FIELD': 'DN',
            'OPERATOR': 0,  # Equals
            'VALUE': 0,
            'OUTPUT': filtered_output
        })

        print(f"Filtered shapefile saved to {filtered_output}")
    except Exception as e:
        print(f"Error processing year {year}: {e}")

#zone statistics of NDVI on the new layer
#the ndvi is for months January, June, September, and March 
#Hence I have to merge each year with each month 

# Define months and their corresponding codes
months = ['January', 'June', 'March', 'Sept']
toCode = {
    'January': '01',
    'June': '06',
    'March': '03',
    'Sept': '09'
}

# Paths
path_rasters = str(LANDUSE) + "/"
path_ndvi = str(NDVI_DIR) + "/"
path_vector = str(CENSO2020 / 'Mexico_Map.shp')

for year in range(2001, 2021):
    for month in months:
        try:
            # Define output file name
            output = f'{path_rasters}ndvi_NoUrban_{year}_{toCode[month]}.xlsx'

            # Check if the output already exists, skip if it does
            if os.path.exists(output):
                print(f"Skipping {output} as it already exists.")
                continue

            # Define input raster file name
            input_raster = f'{path_ndvi}{month}/A{year}.tif'

            # Perform zonal statistics
            processing.run("native:zonalstatisticsfb", {
                'INPUT': f'{path_vector}|layername=Mexico_Map',
                'INPUT_RASTER': input_raster,
                'RASTER_BAND': 1,
                'COLUMN_PREFIX': '_',
                'STATISTICS': [0, 1, 2, 3],  # Min, max, mean, sum
                'OUTPUT': output
            })

            print(f"Zonal statistics saved to {output}")
        except Exception as e:
            print(f"Error processing {year}-{month}: {e}")
            
