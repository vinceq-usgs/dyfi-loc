// Graphics definitions in this section

        var epicenterIcon = L.icon({
            iconUrl : "images/star.png",
            iconSize : 16,
        });

        var solutionMarkerOption = {
                        radius : 4,
                        color : 'black',
                        weight : 1,
                        fillColor : 'blue',                        
                        fillOpacity : 0.8,
                    };  

        var solutionMarkerHighlight = {
                        color : 'red',
                        weight : 4,
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
        var layercontrolLayer;

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

            L.control.mousePosition().addTo(map);
            L.control.scale({imperial:0,maxWidth:200}).addTo(map);
            return map;
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
                    ptLayer = L.geoJson(solution, {
                        pointToLayer: function(f,latlon) {
                            m = L.marker(latlon, {
                                icon:epicenterIcon,
                            });
                            m.on('mouseover',mouseOver);
                            m.on('click',showSolution);
                            return m;
                        }
                    });
                }
                else {
                    ptLayer = L.geoJson(solution, {
                        pointToLayer: function(f,latlon) {
                            m = L.circleMarker(latlon, solutionMarkerOption);
                            m.on('mouseover',mouseOver);
                            m.on('click',showSolution);
                            mappoints[p.t] = m;
                            return m;
                        },
                    });                                                    

                    // Also store this for intra-solution path
                    lineArray.push(coords);
                }          

            // Add to solutions layer
                solutionsArray.push(ptLayer);
            }
            // Now plot solution paths

            if (lineLayer) {
                map.removeLayer(lineLayer);
            } 
            lineLayer = L.polyline(lineArray, solpathOption).addTo(map);

            // Now plot solutions

            if (solutionLayer) {
                map.removeLayer(solutionLayer);
            }
            solutionLayer = L.featureGroup(solutionsArray);
            solutionLayer.addTo(map);
            map.fitBounds(solutionLayer.getBounds());
 
            // Add control checkboxes 

            if (layercontrolLayer) {
                layercontrolLayer.removeFrom(map);
            }
            layercontrolLayer = L.control.layers({},{
               'Solutions':solutionLayer,
                'Lines':lineLayer,
            }).addTo(map);
            console.log('Finished plotting ' + evid + '.');
            var mapLayers = L.layerGroup([solutionLayer,lineLayer]);
            return mapLayers;
        }

        function mouseOver(e) {
            var pt;
            if (e.target) {
                pt = e.target;
            }
            else {
                pt = e;
            }
            p = pt.feature.properties;
            coords = pt.feature.geometry.coordinates;
            var popuptext;
            var reset;
            if (p.is_epicenter) {
                popuptext = "Real epicenter:<br>M" + p.mag
                    + " (" + coords[1] + "," + coords[0] + ")<br>";                 
            }
            else {
                popuptext = "t: " + p.t + " (" + p.npts + " pts)<br>"
                    + "M" + p.mag + " (" + p.ix + "," + p.iy + ")<br>"
                    + "(" + coords[1] + "," + coords[0] + ")<br>"
                    + "resid: " + p.resid; 
            
            }
            infoControl.update(popuptext);            
//            popup = pt.bindPopup(popuptext)
//                .on('popupopen',highlightMarker)
//                .on('popupclose',resetMarker)
 //               .openPopup();

            graphHilight(p.t);
        }

        function highlightMarker(e) {
            pt = e.target;
            p = pt.feature.properties;

            if (p.is_epicenter) {
                return;
            }
            pt.setStyle(solutionMarkerHighlight);
        }

        function resetMarker(e) {
            pt = e.target;
            p = pt.feature.properties;
            if (p.is_epicenter) {
                return;
            }
            pt.setStyle(solutionMarkerOption);
        }

    function drawInfoControl() {
        console.log('in drawInfoControl');
        if (infoControl) {
            infoControl.removeFrom('map'); // This gives error?
        }

        infoControl = L.control({'position':'bottomright'});  
        infoControl.onAdd = function(map) {
            // create a div with a class "info"
            this._div = L.DomUtil.create('div', 'infoControl'); 
            this.update();
            return this._div;
        };
 
// method that we will use to update the control
        infoControl.update = function (text) {
            this._div.innerHTML = "<div class='infoControl'>"+text+"</div>";
        };

        console.log('Adding to map');
        infoControl.addTo(map);
        return infoControl;
    }

    function showSolution(e) {
        console.log(e);
        var pt;
        if (e.target) {
            pt = e.target.feature;
        }
        else if (e.properties) {
            pt = e;
        }
        else {
            return;
        }
        t = pt.properties.t;
        text = 'TODO: Show solution grid for t=' + t;
        infoControl.update(text);
    
    }

             


