# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:24:15 2024

@author: Jos3
"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from config import ROOT, CENSO1990, CENSO2000, CENSO2010, CENSO2020, CORE, NDVI_DIR, LANDUSE, RESULTS


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from unidecode import unidecode 

path = r"C:\Users\Jos3\Documents\Mexico\Thesis argument\API_SI.POV.GINI_DS2_fr_excel_v2_607.xls"

df = pd.read_excel(path, skiprows=3)

df = df[df['Country Code']== 'MEX']
df = pd.melt(
    df, 
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
    value_vars=[str(year) for year in range(1960, 2024)], 
    var_name='Year', 
    value_name='gini'
)

df['Year'] = pd.to_numeric(df['Year'])

# Plot the line graph
plt.figure(figsize=(10, 6))
plt.scatter(df['Year'], df['gini'], color='blue', label='Gini Index')

# Add labels and title
plt.xlabel('Year', fontsize=12)
plt.ylabel('GINI Index', fontsize=12)
plt.title('GINI Index Over Time', fontsize=14)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()

# Only draw x and y axes (hide top and right spines)
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(0.8)
ax.spines['bottom'].set_linewidth(0.8)

# Ensure ticks are visible
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# Display the graph
plt.tight_layout()
exp = str(ROOT / 'Thesis argument/gini_index_scatter.png')
plt.savefig(exp, dpi=300)
plt.show()
