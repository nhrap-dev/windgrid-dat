# windgrid-dat

The windgrid dat scripts take a windgrid and create a Hazus dat file. 

The files windgrid-dat-esri.py and windgrid-dat.py are depreciated and functionality of some functions may be unstable. The replacement will be scripts targeting particular file type conversions (e.g., arcgrid-to-dat.py; gtiff-to-dat.py; csv-to-dat.py; shapefile-to-dat.py)

csv-to-dat.py, shapefile-to-dat.py, and utils.py are still under development and are not functional at this point.

<h2>To use</h2>

1. activate your venv with all dependencies

    Example: activate hazus_env

2. run setup.py to create the database and directories

    Example: python setup.py

3. copy the conversion files to the input folder (GTiff, CSV, Shapefile, ArcGrid)

4. run the script in the terminal

    Syntax: python script.py dat_header_name dat_header_date

    Example: python gtiff-to-dat.py "Hurricane Hanna" 09/08/2020

5. view the .dat file(s) in the output folder


<h2>Notes</h2>

* The open-source scripts utilizes the base data and does not need census tract centroids provided
* The proprietary tool does not utilize the base data and requires census tract centroids to be prepared prior to running
 
