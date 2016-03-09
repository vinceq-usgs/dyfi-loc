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
        var gridMarkerOption = {
                        radius : 2,
                        color : 'black',
                        weight : 1,
                        fillColor : 'green',                        
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

            if (gridLayer) {
                removeGridLayer();
            }


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
                            return m;
                        }
                    });
                }
                else {
                    ptLayer = L.geoJson(solution, {
                        pointToLayer: function(f,latlon) {
                            m = L.circleMarker(latlon, solutionMarkerOption);
                            m.on('mouseover',mouseOver);
                            m.on('click',clickSolution);
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
            var p = pt.feature.properties;
            var coords = pt.feature.geometry.coordinates;
            var popuptext;
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

            highlightMarker(e);
            graphHilight(p.t);
        }

        function highlightMarker(e) {
            var pt;
            if (e.target) { pt = e.target; }
            else { pt = e; }

            if (hilightedpt == e) { return; }

            var p = pt.feature.properties;
            if (p.is_epicenter) { return; }
            pt.setStyle(solutionMarkerHighlight);
            if (hilightedpt && (hilightedpt !== pt)) {
                resetMarker(hilightedpt); 
            }
            hilightedpt = pt;
        }

        function resetMarker(pt) {
            var p = pt.feature.properties;
            if (p.is_epicenter) {
                return;
            }
            pt.setStyle(solutionMarkerOption);
        }

    function drawInfoControl() {
        if (infoControl) {
            infoControl.removeFrom(map); 
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

        infoControl.addTo(map);
        return infoControl;
    }

// Calls by map pt and graph pt have different sources
    function clickSolution(e) {
        var pt;
        if (e.target) { pt = e.target.feature; } else { pt = e; }
        var t = pt.properties.t;
    
        if (t == displayedgrid) {
            console.log('Removing grid.');
            removeGridLayer();
            return;
        }

        removeGridLayer();        
        var text = 'Showing solution grid for t=' + t;
        infoControl.update(text);

       var inputname = 'data/grids/' + evid + '/grid.' + t + '.geojson';
        displayedgrid = t;
        $.getJSON(inputname,onLoadGrid);
    }

    function onLoadGrid(grid) {
        solutionGrid = grid;
        showGrid(grid);
    }
        
    function showGrid(grid) {
        var gridpts = [];

        if (gridLayer && layercontrolLayer) {
            layercontrolLayer.removeLayer(gridLayer);
        }
        for (var i=0; i<grid.features.length; i++) {
            var pt = grid.features[i];
 
            var ptLayer = L.geoJson(pt, {
                pointToLayer: function(f,latlon) {
                    return L.circleMarker(latlon,gridMarkerOption)
                        .on('mouseover',hoverGrid)
                        .on('click',removeGridLayer);
                },
            });                                                    
            gridpts.push(ptLayer);
        }
        gridLayer = L.featureGroup(gridpts).addTo(map);
        gridLayer.addTo(map);
//        map.fitBounds(gridLayer.getBounds());
 
        // Add control checkbox 

        if (layercontrolLayer) {
            layercontrolLayer.addOverlay(gridLayer,'Solution grid');
        }
        return gridLayer;
    }
           
    function hoverGrid(e) {
        var p = e.target.feature.properties;
        var text = '(' + p.ix + ',' + p.iy + ') + M'
             + p.mag + ' resid: ' + p.resid;
        infoControl.update(text);    
    }  
    function removeGridLayer() {
        if (!gridLayer) { return; }
        map.removeLayer(gridLayer);
        layercontrolLayer.removeLayer(gridLayer);
        displayedgrid = undefined;
    }

