
var margin = 50,
    width = 700,
    height = 250;

var x_scale;
var y_scale;

function drawGraphDistance(data) {
    console.log('Now in drawGraphDistance.');
    console.log(data);

    if (svg2) {
        svg2.remove();
    }

    svg2 = d3.select('#graphdistance')
        .append("svg")
        .attr("width", width)
        .attr("height", height);
 
    svg2.selectAll('circle.responses')
        .data(data.features).enter()
        .append('circle').attr('class','responses');

    var x_extent = [5,300];
    var y_extent = [1,9];

    x_scale = d3.scale.log().range([margin,width-margin])
        .domain(x_extent);
    y_scale = d3.scale.linear().range([height-margin,margin])
        .domain(y_extent);

    var x_axis = d3.svg.axis().scale(x_scale).ticks(20, ",.1s");
    var y_axis = d3.svg.axis().scale(y_scale).orient('left');

    svg2.append('g')
        .attr('class','x axis')
        .attr('transform','translate(0,'+(height-margin)+')')
        .call(x_axis).append('text')
        .text('Epicentral distance (km)')
        .attr('x',(width/2)-margin)
        .attr('y',margin/1.5);
    svg2.append('g')
        .attr('class','y axis')
        .attr('transform','translate('+margin+',0)')
        .call(y_axis).append('text')
        .text('Intensity')
        .attr('transform','rotate(-90,-32,0) translate(-180)');

    svg2.selectAll('circle')
        .attr('cx',function(d){return x_scale(d.properties._dist)})
        .attr('cy',function(d){return y_scale(d.properties.cdi)})
        .attr('r',5);



}

function drawGraphIpe(data) {
    console.log('In drawGraphIpe');
    console.log(data);

    var line_ipe = d3.svg.line()
        .x(function(d){
            return (d.x >= 5) ? 
                x_scale(d.x) : x_scale(5)
        })
        .y(function(d){
            return (d.x >= 5) ?
                y_scale(d.y) : y_scale(1)
        });

    svg2.append('path')
        .attr('d',line_ipe(data.values))
        .attr('class','path mag');

}


    function mouseOverPt(e) {
        mappt = mappoints[e.properties.t];
        if (mappt) {
            mouseOver(mappt);
            return;
        }
        if (e.properties.is_epicenter) {
            mouseOver(e);
        }
    }
    
    function graphHilight(e) {
        if (selected) {
        selected.style({
            'stroke':'black',
            'stroke-width':1
            }).attr('r',4);
        }
        var selection = svg.select('#graph_resid_'+e);
        selection.style({'stroke':'red','stroke-width':3}).attr('r',8);
        selected = selection;
    }

