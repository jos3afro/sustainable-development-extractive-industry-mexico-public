# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 09:51:30 2025

@author: Jos3
"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from config import ROOT, CENSO1990, CENSO2000, CENSO2010, CENSO2020, CORE, NDVI_DIR, LANDUSE, RESULTS


import pandas as pd
import glob
import os


# Define the path to the folder containing the Excel files
path = str(LANDUSE) + "/"

# Initialize an empty DataFrame to store the merged data
df = pd.DataFrame()

# Loop through the years
for year in range(2001, 2021):
    file = path + f'UrbanArea_{year}.xlsx'
    
    # Read the Excel file
    temp = pd.read_excel(file)
    
    # Select the relevant columns
    temp = temp[['CVEGEO', '_sum', '_mean']]
    
    # Rename the columns to include the year
    temp.columns = ['CVEGEO', 'LandUse_sum', 'LandUse_mean']
    temp['year'] = year
    
    # Merge with the main DataFrame

    df = pd.concat([df, temp], ignore_index=True) 

# Save the combined DataFrame to a new Excel file
output_file = path + 'LandUse_2001_2020.xlsx'
df.to_excel(output_file, index=False)

print(f"Combined data saved to {output_file}")


################################### Merging data of NDVI excluding urban areas ############################
path = str(LANDUSE) + "/"

output_df = pd.DataFrame()  # Initialize an empty dataframe to store the results

for year in range(2001, 2021):
    # Fetch files for the current year
    file_pattern = os.path.join(path, f"ndvi_NoUrban_{year}*")
    year_files = glob.glob(file_pattern)  # List all files matching the pattern for the year
    
    for file in year_files:
        # Read the data from the file
        temp = pd.read_excel(file)
        
        # Keep only the important columns
        temp = temp[['CVEGEO', '_sum', '_mean', '_median']]
        
        # Rename columns to meaningful names
        temp.columns = ['CVEGEO', 'NDVI_sum', 'NDVI_mean', 'NDVI_median']
        temp['year'] = year  # Add the year as a separate column
        
        # Append the current dataframe to the main output dataframe
        output_df = pd.concat([output_df, temp], ignore_index=True)  # Concatenate dataframes

output_df = output_df.groupby(['CVEGEO', 'year']).agg('mean').reset_index()     

output_file = path + 'NDVI_noUrban2001-2020.xlsx'
output_df.to_excel(output_file, index=False)