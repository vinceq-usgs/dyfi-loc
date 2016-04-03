# dyfi-loc
* Prototype * DYFI locator. Given a batch of DYFI entries (point intensities), determine the earthquake origin. 

The goal is to provide a solution (magnitude, location, time, uncertainty?) as a dyfi-loc product to PDL. This will be used by Hydra to help trigger smaller felt-but-underinstrumented events. Paul also discussed receiving TED location (which should always happen first) as the seed for starting this procedure and initial location.

Location Viewer Installation
---------------

To use the Location Viewer:

1. Install this repository.
2. Start a local HTTP server by entering 'cd leaflet; ./httpserver &'
3. Point your browser to 'http://localhost:8000/results.html

Location Viewer Features
-----
- Use the Event Selector menu in the lower left corner to select an event.
- Hover mouse pointer over solutions in map or graph to see info.
- Click on a solution to show the trial grid that produced that solution. Click again to remove from display.
- Press 'play' on slider bar to see aggregated responses.

Locator Algorithm
---------
1. Load a collection of unassociated individual responses with geocoded location and intensities. 
2. Run aggregator to create geocoded boxes.
3. Determine the location with largest intensity; use that as the starting point. Alternatively, use a weighted (by squared intensity) spatial average. This will be the initial search location.
4. Set up a search grid (possibly related to max int) centered on the initial location.
5. Iterate over each node of the search grid.
6. The next step depends on which residual calculation method is used.
  - Version A (old Locator method):
    1. Iterate over test magnitudes (and depths? depending on IPE):
      1. Assume this node is a "test epicenter" with given magnitude. 
      2. Iterate through each observation and calculate the estimated intensity.
      3. Compare with the actual (observed) intensity at that location.
      4. Sum up the weighted squared residuals of intensity.
    2. The magnitude with the lowest residual is the "best" magnitude for this test epicenter.
  - Version B (B&W method):
    1. Iterate through each observation and calculate the magnitude what would result in this intensity.
    2. Compare each calculated magnitude of each location with the weighted mean of the magnitudes in all locations.
    3. Sum up the weighed variances in magnitude. That is the residual for this test epicenter.
7. Select the node-magnitude combination with the smallest total residual. This is the preferred solution.
8. Test the azimuthal coverage of the observations w.r.t. the solution, reject if insufficient coverage. (TODO)
9. Determine the time of origin using the initial entry time (or some computation of initial entry times) (TODO)

IPEs
----
Atkinson, Worden, and Wald (2014). Intensity Prediction Equations for North America. BSSA Vol. 104, no.6, Dec 2014

Test events
-----------
- ci37372672
- ci15520985
- ci14745580
- ci15296281
- ci15481673
- nc71996906
- nc72282711

Time, load statistics and optimization
-----------------------

Notes on preliminary version
-----------------------
Input is a GeoJSON FeatureCollection file. Features are individual observations as Point Features with property 'user_cdi'. In addition, there is a Point Feature representing the actual epicenter with properties 'magnitude' and 'is_epicenter' (for comparison).

Output is a GeoJSON FeatureCollection file. Features are the 'best guess' epicenters as Point Features at each particular timeframe with properties 'magnitude', 'resid' (residual), 't' (time in seconds past initial observation), and 'npts' (number of points in this dataset).  

LICENSE
-------
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

