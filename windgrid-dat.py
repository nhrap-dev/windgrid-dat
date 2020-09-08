import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from time import time
import rasterio as rio
from shapely.geometry import Point


def idw(kdtree, z, xi, yi):
    """ Inverse Distance Weighting - interpolates an unknown value at a 
    specified point by weighting the values of it's nearest neighbors

    Keyword arguments:
        kdtree: scipy.spatial.ckdtree -- kdtree made from a 2d array of x and y coordinates as the columns 
        z: 1d array -- point values at each location
        xi: float -- x-axis point location of unknown value
        yi: float -- y-axis point location of unknown value

    Returns:
        zi: float -- interpolated value at xi, yi

    """
    neighbors = 12
    power = 2
    distances, indicies = kdtree.query([xi, yi], k=neighbors)
    z_n = z[indicies]
    if 0 not in distances:
        weights = power / distances
    else:
        distances += 0.000000001
        weights = power / distances
    weights /= weights.sum(axis=0)
    zi = np.dot(weights.T, z_n)
    return zi


def create_dat_from_shapefile(windgrid_file, DAT_header, output_file, wind_field='Vg_mph'):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid shapefile

    Keyword arguments:
        windgrid_file: str -- file location of windgrid shapefile
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
    """
    t0 = time()
    output_file = output_file + '.dat'
    print('reading windgrid')
    t1 = time()
    gdf = gpd.read_file(windgrid_file)
    create_dat_from_geodataframe(
        gdf, DAT_header, output_file, wind_field=wind_field)


def create_dat_from_csv(windgrid_file, DAT_header, output_file, wind_field='gust_mph', latitude_field='lat', longitude_field='lon'):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid csv file

    Keyword arguments:
        windgrid_file: str -- file location of windgrid csv
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
        latitude_field: str -- the column or field name for the latitude coordinates (use WGS84)
        longitude_field: str -- the column or field name for the longitude coordinates (use WGS84)
    """
    df = pd.read_csv(windgrid_file)
    df['geometry'] = [Point(x, y) for x, y in zip(
        df[longitude_field], df[latitude_field])]
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    create_dat_from_geodataframe(
        gdf, DAT_header, output_file, wind_field=wind_field)


def create_dat_from_raster(raster):
    # TODO --- NOT DONE --- finish coding
    """ Creates a Hazus DAT file containing windspeeds in m/s from a geopandas geodataframe

    Keyword arguments:
        gdf: str -- a geodataframe containing a point windgrid and windspeeds
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
    """
    band = rio.open(raster)


def create_dat_from_geodataframe(gdf, DAT_header, output_file, wind_field='gust_mph'):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a geopandas geodataframe

    Keyword arguments:
        gdf: str -- a geodataframe containing a point windgrid and windspeeds
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
    """
    t0 = time()
    t1 = time()
    centroids_all = gpd.read_file('base_data/us_centroids.shp')
    buff = gdf.geometry.buffer(0.2)
    buff_gdf = gpd.GeoDataFrame(geometry=buff.geometry)
    buff_gdf['dis'] = 1
    dissolve = buff_gdf.dissolve(by='dis')
    centroids_intersect = centroids_all.intersects(dissolve.unary_union)
    centroids = centroids_all[centroids_intersect == True]
    print(time() - t1)

    print('formatting data for idw')
    t1 = time()
    xy = np.asarray([[x.x, x.y] for x in gdf.geometry])
    z = np.asarray([x for x in gdf[wind_field]])
    xis = np.asarray([x.x for x in centroids.geometry])
    yis = np.asarray([x.y for x in centroids.geometry])
    print(time() - t1)

    print('interpolating values')
    t1 = time()
    kdtree = cKDTree(xy)
    zis = []
    for xi, yi in zip(xis, yis):
        zi = idw(kdtree, z, xi, yi)
        zis.append(zi)
    print(time() - t1)
    zis = np.asarray(zis)
    zis = zis * 0.44704

    print('formatting dataframe for output')
    t1 = time()
    tracts = list(map(lambda x: x + '    ', centroids.FIPS))
    longs = list(map(lambda x: '{0:.4f}'.format(x) + '   ', xis))
    lats = list(map(lambda x: '{0:.4f}'.format(x) + '      ', yis))
    windSpeeds = list(map(lambda x: '{0:.5f}'.format(x) + '     ', zis))
    zeros = list(map(lambda x: '0' + '{0:.5f}'.format(x * 0) + '    ', zis))
    windSpeedsLast = list(map(lambda x: '{0:.5f}'.format(x), zis))
    df = pd.DataFrame({'tracts': tracts, 'longs': longs, 'lats': lats,
                       'windSpeeds': windSpeeds, 'zeros': zeros, 'windSpeedsLast': windSpeedsLast})
    print(time() - t1)

    print('writing output DAT file')
    t1 = time()
    # creates and opens the export DAT file
    pd.DataFrame().to_csv(output_file, header=False, index=False)
    export = open(output_file, "w")

    # adds columns to the DAT file header
    DAT_header.append('')
    DAT_header.append(
        '      ident        elon      nlat         ux          vy        w (m/s)')

    # writes header to DAT file
    for row in DAT_header:
        export.write(row + '\n')

    # writes data to DAT file
    for row in range(len(df[df.columns[0]])):
        writeRow = ''
        for item in df.iloc[row]:
            writeRow = writeRow + item
        export.write(writeRow + '\n')
    export.close()
    print(time() - t1)
    print('Total elasped time: ' + str(time() - t0))


windgrid_file = r'C:\projects\Disasters\2020_Laura\ARA_0908\Hurricane Laura Rapid Response Windfield Release 3/3-Hurricane_Laura_Simulated_Winds_Release_3.csv'
DAT_header = ['Laura 2020: ARA Wind Model as of 09/08/2020',
              'PEAK 3-SECOND GUSTS AT 10 M OVER FLAT, OPEN TERRIAN',
              'Swath domain provided by FEMA']
# 'Landfall position:     -77.8001      34.2001']
output_file = 'C:/projects/Disasters/2020_Laura/ARA_0908/windgrid.dat'

create_dat_from_csv(windgrid_file, DAT_header,
                    output_file, wind_field='gust_mph')
