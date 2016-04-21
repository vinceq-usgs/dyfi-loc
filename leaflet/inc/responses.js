
var responseMarkerOption = {
    radius : 2,
    weight : 1,
    color : 'black',
    fillColor : 'green',
    fillOpacity : 1.0,
};

var colorsCdi = {
    9 : '#ec2516',
    8 : '#ff701f',
    7 : '#fdca2c',
    6 : '#f7f835',
    5 : '#95f879',
    4 : '#7efbdf',
    3 : '#82f9fb',
    2 : '#dfe6fe',
    1 : 'white',
};

var tfirst = 1;
var tlast = 1200;

// Responses display

function drawResponses() {

    if (responsesLayer) {
        responsesLayer.clearAllEventListeners();
        map.removeLayer(responsesLayer);
    }

    if (timeControl) {
        timeControl.removeFrom(map);
        map.removeLayer(timeControl);
    }

    timeControl = L.timelineSliderControl({
        start : tfirst,
        end : tlast,
    });
 
    responsesArray = [];
    console.log('Drawing ' + responsesdata.features.length + ' points.')
    responsesLayer = L.timeline(responsesdata, {
        getInterval : function(e) {
            var tfirst = e.properties.t;
            if (tfirst > tlast) { tfirst = tlast; }
            return { start:tfirst, end:tlast };
        },
        pointToLayer: function(e,latlon) {
            var cdi = parseInt(e.properties.cdi);

            var options = [];
            for (var prop in responseMarkerOption) {
                options[prop] = responseMarkerOption[prop];
            }
//            console.log('Got ' + cdi + ' ' + colorsCdi[cdi]);
            options['fillColor'] = colorsCdi[cdi];
            return L.circleMarker(latlon,options)
                .on('click',clickResponse);
        },
    });
    timeControl.addTo(map);
    timeControl.addTimelines(responsesLayer);
    responsesLayer.addTo(map).bringToBack();
    responsesLayer.on('change',function(e) {
        var t = e.target.time;
        checkSolutions(t);
        drawPlotTimeline(t);
        tnow = t;
    });
    timeControl.setTime(tlast);
    if (layercontrolLayer) {
        layercontrolLayer.addOverlay(responsesLayer,'Geocoded responses');
    }
    return(responsesLayer);
}

function clickResponse(e) {
    console.log(e.target.feature.properties);
}

