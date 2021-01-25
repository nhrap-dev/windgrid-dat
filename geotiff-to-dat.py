import geopandas as gpd
import rasterio as rio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from rasterio.features import shapes
from rasterio.mask import mask
from shapely.geometry import shape
from shapely.ops import cascaded_union
import os
import pandas as pd
import sys
from datetime import datetime
from utils import write_dat_file, mph_to_mps
from config import dat_header, input_dir, output_dir

def getValueMask(src):
    mask = None
    image = src.read(1) # first band
    nonZeroMask = np.where(image > 0, 1, 0)
    _shapes = [shape(s) for s, v in shapes(nonZeroMask, transform=src.transform) if v > 0]
    union = cascaded_union(_shapes)
    return union

def generate_dat_df(src, tracts):
        df = pd.DataFrame()
        for index, tract in enumerate(list(tracts.geometry)):
            rasterMask, rasterMaskTransform = mask(dataset=src, shapes=[tract], all_touched=False, crop=True, nodata=0)
            mean = np.mean(rasterMask[0])
            mean = mph_to_mps(mean)
            if mean > 0:
                df = df.append({
                    'ident': f"{tracts.loc[index]['GEOID']}    ",
                    'elon': f"{'{0:.4f}'.format(float(tracts.loc[index]['geometry'].centroid.x))}   ",
                    'nlat': f"{'{0:.4f}'.format(float(tracts.loc[index]['geometry'].centroid.y))}      ",
                    'ux': f"{'{0:.5f}'.format(mean)}     ",
                    'vy': f"0{'{0:.5f}'.format(0)}    ",
                    'w (m/s)': f"{'{0:.5f}'.format(mean)}",
                }, ignore_index=True)
        
        df = df.reindex(columns=['ident', 'elon', 'nlat', 'ux', 'vy', 'w (m/s)'])
        return df

def geotiff_to_dat():
    rasters = [x for x in os.listdir(input_dir) if x.endswith('.tif')]
    tracts = gpd.read_file('db/tracts/tracts.shp')
    for raster in rasters:
        src = rio.open(f'{input_dir}/{raster}')
        valueMask = getValueMask(src)
        intersect = tracts.geometry.intersects(valueMask)
        tractsSelection = tracts[intersect]
        tractsSelection = tractsSelection.reset_index()
        df = generate_dat_df(src, tractsSelection)
        output_file = f'{output_dir}/{raster}.dat'
        write_dat_file(output_file, df, dat_header)


if __name__=='__main__':
    geotiff_to_dat()