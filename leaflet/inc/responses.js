
var responseMarkerOption = {
    radius : 2,
    weight : 0,
    fillColor : 'green',
    fillOpacity : 0.5
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
            return { start:e.properties.t, end:tlast };
        },
        pointToLayer: function(e,latlon) {
            return L.circleMarker(latlon,responseMarkerOption);
        },
    });
    timeControl.addTo(map);
    timeControl.addTimelines(responsesLayer);
    responsesLayer.addTo(map).bringToBack();
    responsesLayer.on('change',function(e) {
        drawPlotTimeline(e.target.time);
    });
    timeControl.setTime(tlast);
    if (layercontrolLayer) {
        layercontrolLayer.addOverlay(responsesLayer,'Geocoded responses');
    }
    return(responsesLayer);
}


