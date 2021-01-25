import arcpy
from arcpy.sa import *
import pandas as pd
from time import time
arcpy.CheckOutExtension('Spatial')

def printElapsedTime(message, t0):
    if (time() - t0) > 3600:
        print(message + '... at ' + str(round((time() - t0)/3600, 4)) + ' hours')
    if (time() - t0) > 60:
        print(message + '... at ' + str(round((time() - t0)/60, 3)) + ' minutes')
    else:
        print(message + '... at ' + str(round(time() - t0, 2)) + ' seconds')

def generateWindSpeedDAT(input_windgrid, input_centroids, input_DAT_header, output_DAT):
    """ Generates DAT file for Hazus

    Keyword arguments:
        input_windgrid: str; ESRI feature class
        input_centroids: str; ESRI feature class
        input_DAT_header: list<str>
    
    Output:
        output_DAT<output>: string; relative or absolute path with output file name
    """
    t0 = time()
    # interpolates the wind speeds
#    idw = Idw(input_windgrid, 'Vg_mph')
    idw = Idw(input_windgrid, 'Vg_mph')
    printElapsedTime('Wind speed interpolation complete', t0)
    # adds the wind speeds to the census tract centroids
    ExtractValuesToPoints(input_centroids, idw, 'in_memory/windSpeedCentroids')
    printElapsedTime('Values extracted to centroids', t0)
    
    # creates a dataframe with only the necessary fields
    fields = ('TRACT', 'CenLongit', 'CenLat', 'RASTERVALU')
    df = pd.DataFrame(arcpy.da.FeatureClassToNumPyArray('in_memory/windSpeedCentroids', fields))
    # changes mph to m/s
    df['RASTERVALU'] = df['RASTERVALU'] * 0.44704
    # formats the data with appropriate spacing for HAZUS
    tracts = list(map(lambda x: x + '    ', df.TRACT))
    longs = list(map(lambda x: '{0:.4f}'.format(x) + '   ', df.CenLongit))
    lats = list(map(lambda x: '{0:.4f}'.format(x) + '      ', df.CenLat))
    windSpeeds = list(map(lambda x: '{0:.5f}'.format(x) + '     ', df.RASTERVALU))
    zeros = list(map(lambda x: '0' + '{0:.5f}'.format(x * 0) + '    ', df.RASTERVALU))
    windSpeedsLast = list(map(lambda x: '{0:.5f}'.format(x), df.RASTERVALU))
    # organizes the newly formatted data into a dataframe
    dfout = pd.DataFrame({'tracts': tracts, 'longs': longs, 'lats': lats, 'windSpeeds': windSpeeds, 'zeros': zeros, 'windSpeedsLast': windSpeedsLast})
    dfout = dfout[['tracts', 'longs', 'lats', 'windSpeeds', 'zeros', 'windSpeedsLast']]
    
    # creates and opens the export DAT file
    pd.DataFrame().to_csv(output_DAT, header=False, index=False)
    export=open(output_DAT, "w")
    
    # adds columns to the DAT file header
    input_DAT_header.append('')
    input_DAT_header.append('      ident        elon      nlat         ux          vy        w (m/s)')
    printElapsedTime('Data formatted for export', t0)
    
    # writes header to DAT file
    for row in input_DAT_header:
        export.write(row + '\n')
    
    # writes data to DAT file
    for row in range(len(dfout[dfout.columns[0]])):
        writeRow = ''
        for item in dfout.iloc[row]:
            writeRow = writeRow + item
        export.write(writeRow + '\n')
    export.close()
    
    # clears in memory workspace
    arcpy.Delete_management('in_memory')
    # resets the input_DAT_header
    input_DAT_header = input_DAT_header[0:-2]
    printElapsedTime('Total elapsed time', t0)

    
# set environment workspace ↓
arcpy.env.workspace = r'C:\Users\jrainesi\Desktop\test'

#  set inputs ↓
input_windgrid = r'H:\Events\National\Nate_2017\Data\Wind\ARA\ARA_Nate_Final\GISDATA/Nate_grid_ver7.shp'
input_centroids = r'C:\data/us_tract_centroids_project.shp'

# construct the DAT file header !do not modify spaces in the landfall position! ↓
input_DAT_header = ['Florence 2018: ARA Day7 as of 09/21/2018',
'MAXIMUM 3 SECOND WINDS AT 2010 CENSUS TRACK CENTROIDS FOR OPEN TERRAIN',
'Swath domain provided by FEMA',
'Landfall position:     -77.8001      34.2001']
# 5 spaces after 'Landfall position' and 6 spaces between coordinates

# set output ↓
output_DAT = r'C:\Users\jrainesi\Desktop\test/nate_o.DAT'

# execute function ☼
generateWindSpeedDAT(input_windgrid, input_centroids, input_DAT_header, output_DAT)
