# windgrid-dat

The windgrid dat scripts take a windgrid and create a Hazus .dat file. 

The replacement will be scripts targeting particular file type conversions (e.g., arcgrid-to-dat.py; gtiff-to-dat.py; csv-to-dat.py; shapefile-to-dat.py)

csv-to-dat.py, shapefile-to-dat.py, and utils.py are still under development and are not functional at this point.

<h2>Setup</h2>

1. activate your venv with all dependencies

    Example: `activate hazus_env`

2. run setup.py to create the database and directories

    Example: `python setup.py`

<h2>To use</h2>

1. Activate your venv with all dependencies

    Example: `activate hazus_env`

2. Copy the files to converst into the input folder (Tiff, CSV, Excel, Shapefile, ArcGrid)

3. Update the variables in `config.py`. The `dat_header` variable will need to be updated for any script. The `latitude_field`, `longitude_field`, and `wind_field` variables will need to be updated for `csv-to-dat.py` and `shapefile-to-dat.py`.

4. Run the script in the terminal

    Syntax: `python script.py`

    Example: `python geotiff-to-dat.py`

5. View the .dat file(s) in the output folder

<h2>Depreciation Warning (Archive)</h2>

* The files windgrid-dat-esri.py and windgrid-dat.py in the archive directory are depreciated and functionality of some functions may be unstable. 