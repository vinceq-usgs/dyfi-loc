# dyfi-loc
DYFI locator. Given a batch of DYFI entries (point intensities), determine the earthquake origin. 

The goal is to provide a solution (magnitude, location, time, uncertainty?) as a dyfi-loc product to PDL. This will be used by Hydra to help trigger smaller felt-but-underinstrumented events. Paul also discussed receiving TED location (which should always happen first) as the seed for starting this procedure and initial location.

Procedure
---------
1. Load a collection of unassociated individual responses with location (geocoded) and intensities. These will be "stations".
2. Determine the location with largest intensity; use that as the starting point. Alternatively, use a weighted (by squared intensity) spatial average. This will be the initial search location.
3. Set up a search grid (possibly related to max int) centered on the initial location.
4. Iterate over each node of the search grid:
5. Iterate over test magnitudes (and depths? depending on IPE):
  - Assume this node is a "test epicenter" with given magnitude. 
  - Iterate through each station and calculate the estimated intensity there. 
  - Sum up the (weighted)? squared residuals for that magnitude.
7. At each node, determine the magnitude with the smallest total residual.
8. Select the node-magnitude combination with the smallest total residual. This is the preferred solution.
9. Test the azimuthal coverage of the stations w.r.t. the solution, reject if insufficient coverage.
10. Determine the time of origin using the initial entry time (or some computation of initial entry times)

IPEs
----

Test events
-----------

Time, load statistics and optimization
-----------------------

