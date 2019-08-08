# windgrid-dat

The windgrid dat scripts take a windgrid and create a Hazus dat file. 

This repo contains:
  - [x] a proprietary script using ESRI's ArcPy and spatial extension
  - [x] an open-source script
  - [x] base data tract centroids


<h2>Notes</h2>

* The proprietary script runs very fast, cerca 10 seconds, but needs to be updated to retain the leading zeroes on the tract IDs.
* The open-source script run very slow, cerca 20 minutes. The idw algorithm is incredibly slow and needs to be updated.

<h2>To use</h2>

1. Scroll to the bottom of the script and replace the inputs
2. Run the whole script

If you are using the proprietary script, you will need to refine the tract centroids prior to running it. The open-source utilized the base data and refines the extent in the function.
 
