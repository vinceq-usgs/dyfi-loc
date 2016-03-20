
// Graphics definitions in this section

var gridColorsDiffMag = {
    2.33 : '#800026',
    2.0 : '#E31A1C' ,
    1.66 : '#FC4E2A' ,
    1.33 : '#FD8D3C' ,
    1.0 : '#FEB24C' ,
    0.66 : '#FED976' ,
    0.33 : '#FFEDA0' ,
    '-0.1' : 'white',
    '-0.2' : '#d0d1e6' ,
    '-0.3' : '#a6bddb' ,
    '-0.4' : '#74a9cf' ,
    '-0.5' : '#3690c0' ,
    '-0.6' : '#0570b0' ,
    '-0.7' : '#045a8d' ,
    '-999' : '#023858',
    title : '+/- diff M',
}
var gridColorsResid = {
    '3.5' : '#800026',
    '3.0' : '#E31A1C' ,
    '2.5' : '#FC4E2A' ,
    '2.0' : '#FD8D3C' ,
    '1.5' : '#FEB24C' ,
    '1.0' : '#FED976' ,
    '0.5' : '#FFEDA0' ,
    '0.0' : 'white',
    title : 'Resid',
}
var gridColors = gridColorsResid;

        var epicenterIcon = L.icon({
            iconUrl : "images/star.png",
            iconSize : 16,
        });

        var solutionMarkerOption = {
            radius : 4,
            color : 'black',
            weight : 1,
            fillColor : 'blue',                        
            fillOpacity : 1.0,
                    };

       var gridMarkerOption = {
            radius : 3,
            color : 'black',
            weight : 1,
            fillColor : 'white',                        
            fillOpacity : 1.0,
        }

        var solutionMarkerHilight = {
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

            L.control.mousePosition({position:'bottomright'}).addTo(map);
            L.control.scale({imperial:0,maxWidth:200}).addTo(map);
            return map;
        }
// Map functions

        function drawMap() {
            data = solutionsdata;
            solutionsArray = [];
            lineArray = [];

            if (gridLayer) { removeGridLayer(); }

            console.log('Drawing ' + data.features.length + ' points.')
            for (i=0; i<data.features.length; i++) {
                solution = data.features[i];
                p = solution.properties;
                var popuptext;
                var ptLayer;
                isEpicenter = solution.properties.is_epicenter;
                if (isEpicenter) {
                    epicenterpt = solution;
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
                    // Reverse this since geojson format is (lon,lat)
                    // and leaflet format is (lat,lon)
                    coords = solution.geometry.coordinates.slice().reverse();
                    lineArray.push(coords);
                }          

                // Add to solutions layer
                // Note epicenter is part of solutions layer
                solutionsArray.push(ptLayer);
            }

            // Now plot solution paths

            if (lineLayer) {
                map.removeLayer(lineLayer);
            } 
            lineLayer = L.polyline(lineArray,solpathOption).addTo(map);

            // Now plot solutions on top of path

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
            var p;
            var coords;
            if (e.target) {
                pt = e.target;
                f = pt.feature;
            }
            else if (e.feature) {
                pt = e;
                f = e.feature;
            }
            else { f = e; }
            p = f.properties;
            coords = f.geometry.coordinates.slice();

            var text;
            if (p.is_epicenter) {
                text = "Actual event params:<br>M" + p.mag
                    + " (" + coords[1] + "," + coords[0] + ")";                 
                infoControl.update(text);            
                return; 
            }
            text = "t: " + p.t + " (" + p.npts + " pts)<br>"
                + "Best magnitude: M" + p.mag + "<br>"
                + "(" + coords[1] + "," + coords[0] + ")<br>"
                + "resid: " + p.resid + '<br>'
                + 'Click point to see trial grid'; 
            infoControl.update(text);            

            hilightMarker(e);
            graphHilight(p.t);
        }

        function hilightMarker(e) {
            var pt;
            if (e.target) { pt = e.target; }
            else { pt = e; }

            if (hilightedpt == e) { return; }

            var p = pt.feature.properties;
            if (p.is_epicenter) { return; }
            pt.setStyle(solutionMarkerHilight);
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
    
        if (pt == gridparentpt) {
            removeGridLayer();
            return;
        }

        var text = 'Showing solution grid for t=' + t + '<br>'
            + 'Mouseover point to see stats';
        infoControl.update(text);

        gridparentpt = pt;
        var inputname = 'data/grids/' + evid + '/grid.' + t + '.geojson';
        $.getJSON(inputname,onLoadGrid);
    }

    function onLoadGrid(griddata) {
        if (gridLayer) {
            // removeGridLayer will clobber gridparentpt; save it
            var savept = gridparentpt;
            removeGridLayer();
            gridparentpt = savept;
        }
        showGrid(griddata);
        trialgriddata = griddata;
        solutionLayer.bringToFront();
    }
        
    function showGrid(griddata) {
        var gridpts = [];

        // Remove old gridLayer if necessary

        if (gridLayer && layercontrolLayer) {
            layercontrolLayer.removeLayer(gridLayer);
        }

        // Now create new gridLayer and display it

        for (var i=0; i<griddata.features.length; i++) {
            var pt = griddata.features[i];
 
            var ptLayer = L.geoJson(pt, {
                pointToLayer: function(f,latlon) {
                    return L.circleMarker(latlon,setGridMarkerStyle(f))
                        .on('mouseover',hoverGrid)
                        .on('click',removeGridLayer);
                },
            });                                                    
            gridpts.push(ptLayer);
        }
        gridLayer = L.featureGroup(gridpts).addTo(map);

        // If this is the first gridLayer, reset bounds to fit

        if (!trialgriddata) {
            map.fitBounds(gridLayer.getBounds());
        }
        gridLayer.addTo(map);
 
        // Add control checkbox 

        if (layercontrolLayer) {
            layercontrolLayer.addOverlay(gridLayer,'Trial grid');
        }

        // Add gridcolor legend

        if (!gridLegend) {
            gridLegend = L.control({position: 'bottomleft'});
            gridLegend.onAdd = function(map) {
                var div = L.DomUtil.create('div', 'info legend');

                var sorted = gridColors.sortedkeys;
                div.innerHTML = gridColors.title + '<br>';
        
                for (var i = 0; i <  gridColors.length; i++) {
                    var key = sorted[i];
                    var color = gridColors[key];
                    div.innerHTML +=
            '<i style="background:' + color + '"></i> ' + key + '<br>';
                }
                return div;
            }
            gridLegend.addTo(map);
        }
    }
           
    function hoverGrid(e) {
        var p = e.target.feature.properties;
        var text = '(' + p.ix + ',' + p.iy + ')<br>'
            + 'M' + p.mag + ' (weighted mean)<br>resid: ' + p.resid + '<br>'
            + '<br>Click any point to remove grid';
        infoControl.update(text);    
    } 
 
    function removeGridLayer() {
        if (!gridLayer) { return; }
       layercontrolLayer.removeLayer(gridLayer);
        map.removeLayer(gridLayer);
        
        if (gridLegend) { gridLegend.removeFrom(map); }

        gridLegend = undefined;
        gridparentpt = undefined;
    }

    function switchGrid(type) {
        if ((type == 'resid') && (gridColors !== gridColorsResid)) {
            gridColors = gridColorsResid;
            if(trialgriddata) { onLoadGrid(trialgriddata); }
            return;
        } 
        if ((type == 'diffmag') && (gridColors !== gridColorsDiffMag)) {
            gridColors = gridColorsDiffMag;
            if(trialgriddata) { onLoadGrid(trialgriddata); }
            return;
        } 
    }

    function setGridMarkerStyle(f) {
        var v = (gridColors === gridColorsResid) ? v = f.properties.resid
            : (f.properties.mag - gridparentpt.properties.mag);
        var color = hash(v,gridColors);

        options = {};
        for (var prop in gridMarkerOption) {
            options[prop] = gridMarkerOption[prop];
        }
        options['fillColor'] = color;

        return options;
    }

// Javascript doesn't have sorted dict, use this instead

function hash(v,obj) {
    if (!obj.sortedkeys) {
        var sortedkeys = [];
        for (var key in obj) {
            if (key=='sortedkeys') { continue; }
            if (!obj.hasOwnProperty(key)) { continue; }
            if (key=='title') { continue; }
            sortedkeys.push(key);
        }
        sortedkeys.sort(function(a,b){return parseFloat(b)-parseFloat(a)});
        obj.sortedkeys = sortedkeys;
        obj.length = sortedkeys.length;
    }
    for (var i=0; i<obj.sortedkeys.length; i++) {
        var key = obj.sortedkeys[i];
        if (v >= parseFloat(key)) {
            return obj[key];
        }
    }
    console.log('WARNING: Out of bounds value ' + v);
    var key = obj.sortedkeys[obj.length - 1];
    return obj[key];
}


