# modify the text that will appear in the head of the .dat file
# each item in the array will appear as a new row
dat_header = [
    'Hurricane Whatever: ARA Wind Model as of 01/25/2021',
    'PEAK 3-SECOND GUSTS AT 10 M OVER FLAT, OPEN TERRIAN',
    'Swath domain provided by FEMA'
]

# configure the field names (applicable for: csv-to-dat and shapefile-to-dat)
latitude_field = 'Lat'
longitude_field = 'lon'
wind_field = 'vg_mph'

# NOT RECOMMENDED TO UPDATE - input/output directories
input_dir = 'input'
output_dir = 'output'