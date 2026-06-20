# -*- coding: utf-8 -*-
"""
Land use download from NASA LP DAAC (MCD12C1 product)
Requires a free NASA Earthdata account: https://urs.earthdata.nasa.gov
Set your token as an environment variable: NASA_EARTHDATA_TOKEN
"""

import os
import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ROOT, LANDUSE

# Set your NASA Earthdata token as an environment variable:
#   Windows: $env:NASA_EARTHDATA_TOKEN = "your-token"
#   Linux/Mac: export NASA_EARTHDATA_TOKEN="your-token"
token = os.environ.get('NASA_EARTHDATA_TOKEN')
if not token:
    raise EnvironmentError(
        "NASA_EARTHDATA_TOKEN environment variable not set. "
        "Get a free token at https://urs.earthdata.nasa.gov"
    )

folder = str(LANDUSE) + "/"
data = ROOT / "LandUse" / "nasa_data.txt"

with open(data, 'r') as algo:
    lines = [line.strip() for line in algo.readlines()]

counter = 0

for url in lines:
    file_name = url.split('/')[-1]
    data_path = Path(os.path.join(folder, file_name))
    counter += 1

    if os.path.isfile(data_path):
        print(f'File already exists: {file_name} ({counter}/{len(lines)})')
    else:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                with open(data_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
            print(f'Downloaded: {file_name} ({counter}/{len(lines)})')
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {file_name}: {e}")
