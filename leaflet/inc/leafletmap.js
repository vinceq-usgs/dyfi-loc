// Graphics definitions in this section

        var epicenterIcon = L.icon({
            iconUrl : "images/star.png",
            iconSize : 16,
        });

        var solutionMarkerOption = {
                        color : '#00f',
                        radius : 4,
                        fillOpacity : 0,
                    };  

        var solpathOption = {
                    color:'blue',
                    weight:2,
                    opacity:0.5,
                    dashArray:'10,10',
                }

// Javascript functions in this section

        var solutionLayer;
        var lineLayer;
        var layersLayer;

        function initmap() {
// set up the map
            map = new L.Map('map');

// create the tile layer with correct attribution
            var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
            var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
            var osm = new L.TileLayer(osmUrl, {minZoom: 4, maxZoom: 16, attribution: osmAttrib});		

// start the map in Southern California
            map.setView([34.0, -118.0],8);
            map.addLayer(osm);
        }
        // Map functions

        function drawMap() {
            data = solutionsData;
            solutionsArray = [];
            lineArray = [];

            for (i=0; i<data.features.length; i++) {
                solution = data.features[i];
                p = solution.properties;
                // Have to reverse this since geojson format is (lon,lat)
                // and leaflet format is (lat,lon)
                coords = solution.geometry.coordinates.slice().reverse();

                var popuptext;
                var ptLayer;
                isEpicenter = solution.properties.is_epicenter;
                if (isEpicenter) {
                    popuptext = "Real epicenter: M" + p.mag;
                    ptLayer = L.geoJson(solution, {
                        pointToLayer: function(feature,latlon) {
                            return L.marker(latlon, { icon:epicenterIcon});
                        }
                    });
                }
                else {
                    popuptext = "t: " + p.t + " (" + p.npts + " pts)<br>"
                        + "M" + p.mag + " (" + p.ix + "," + p.iy + ")<br>"
                        + "(" + coords[1] + "," + coords[0] + ")<br>"
                        + "resid: " + p.resid; 

                    ptLayer = L.geoJson(solution, {
                        pointToLayer: function(feature,latlon) {
                            return L.circleMarker(latlon, solutionMarkerOption);
                        }
                    });
                    
                    // Also store this for intra-solution path
                    lineArray.push(coords);
                }          

            // Add to solutions layer

                ptLayer.bindPopup(popuptext);
                solutionsArray.push(ptLayer);
            }

            // Now plot solutions

            if (solutionLayer) {
                map.removeLayer(solutionLayer);
            }
            solutionLayer = L.featureGroup(solutionsArray);
            solutionLayer.addTo(map);
            map.fitBounds(solutionLayer.getBounds());
 
            // Now plot solution paths

            if (lineLayer) {
                map.removeLayer(lineLayer);
            } 
            lineLayer = L.polyline(lineArray, solpathOption).addTo(map);

            // Add control checkboxes 

            if (layersLayer) {
                layersLayer.removeLayer(solutionLayer);
                layersLayer.removeLayer(lineLayer);
            }
            else {
                layersLayer = L.control.layers({},{
                   'Solutions':solutionLayer,
                    'Lines':lineLayer,
                }).addTo(map);
            }
            console.log('Finished plotting ' + evid + '.');
        }



