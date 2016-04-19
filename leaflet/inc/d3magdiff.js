// In d3magdiff.js

var svgmagdiff;
var margin = 50,
    width = 500,
    height = 350;

var filtertype = 'all';

function drawMagDiff() {
    var xmin = 2.5, xmax = 6.0, ymin = -2, ymax = 2, medianstep = 0.2;
//    var xmin = 1, xmax = 9999, ymin = -2, ymax = 3, medianstep = 500;

    var svg = svgmagdiff;
    console.log('Now in drawMagDiff.');
    if (!svg) {
        svg = d3.select('#graphMagDiff')
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        svgmagdiff = svg;
    }
    else {
        console.log('Removing drawMagDiff.');
        svg.selectAll('*').remove();
    }
    svg.xmin = xmin;
    svg.xmax = xmax;
    svg.ymin = ymin;
    svg.ymax = ymax;
    svg.medianstep = medianstep;

    svg.selectAll('circle.events')
        .data(alldata).enter()
        .append('circle').attr('class','events');

    var x_extent = [xmin,xmax];
    var y_extent = [ymin,ymax];

    x_scale = d3.scale.linear().range([margin,width-margin])
        .domain(x_extent);
    y_scale = d3.scale.linear().range([height-margin,margin])
        .domain(y_extent);

    svg.x_scale = x_scale;
    svg.y_scale = y_scale;

    var x_axis = d3.svg.axis().scale(x_scale).ticks(20, ",.1s");
    var y_axis = d3.svg.axis().scale(y_scale).orient('left');

    svg.append('g')
        .attr('class','x axis')
        .attr('transform','translate(0,'+(height-margin)+')')
        .call(x_axis).append('text')
        .text('Event magnitude')
        .attr('x',(width/2)-margin)
        .attr('y',margin/1.5);
    svg.append('g')
        .attr('class','y axis')
        .attr('transform','translate('+margin+',0)')
        .call(y_axis).append('text')
        .text('M(derived) - M(recorded)')
        .attr('transform','rotate(-90,-32,0) translate(-250)');

/////
    var zero = [
      { 'x':xmin, 'y':0},
      { 'x':xmax, 'y':0}
    ];
    var line = d3.svg.line()
        .x(function(d,i) {
            var x = d.x;
            if (x < svg.xmin) { x = svg.xmin; }
            return svg.x_scale(x);
        })
        .y(function(d) {
            return svg.y_scale(d.y);
        })
    svg.append('path')
        .attr('d',line(zero))
        .attr('id','path_conf_50');


/////

    svg.selectAll('circle.events')
        .filter(function(d) {
            return ((d.npts >= 100) && (d.magdiff<=ymax) && (d.magdiff>=ymin))
        })
        .filter(function(d) { return filterbytype(d)})
        .attr('cx',function(d){return x_scale(d.mag)})
        .attr('cy',function(d){return y_scale(d.magdiff)})
        .attr('class',function(d){return ('circle events ' + d.region)})
        .attr('r',5)
        .on('click',function(d){console.log(d)});

    var rawdata = [];
    $.each(alldata,function(i,d){
        if(!filterbytype(d)) { return; }
        rawdata.push({ 'x':d.mag, 'y':d.magdiff});
    });
    drawMedian(svg,rawdata);
//    confintervals = [ 90,67,50 ];
//    for (var i=0; i <confintervals.length; i++) {
//        drawConfidence(svg,confintervals[i],rawdata);
//        drawConfidence(svg,confintervals[i],rawdata,true);
//    }
}

function drawMedian(svg,rawdata) {
    var mediandata = getmedian(svg,rawdata);
    svg.selectAll('circle.median')
        .data(mediandata).enter()
        .append('circle').attr('class','median')
        .filter(function(d){return d.x>=svg.xmin})
        .attr('cx',function(d){return svg.x_scale(d.x)})
        .attr('cy',function(d){return svg.y_scale(d.y)})
        .attr('class','median')
        .attr('r',5)
        .on('click',function(d){console.log(d)});
}

function getmedian(svg,data) {
    var hashdata = {};
    var results = [];
    var step = svg.medianstep;
    $.each(data,function(i,d){
        var x = d.x, y=d.y;
        if ((y>svg.ymax) || (y<svg.ymin)) { return; }
        for (a=svg.xmin; a<svg.xmax; a = parseFloat((a+step).toFixed(2))) {
            if (a+(step/2) <= x) { continue; }
            var index = a.toString();
            if (hashdata.hasOwnProperty(index)) {
                hashdata[index].push(y);
            }
            else {
                hashdata[index] = [ y ];
            }
            break;
       }
    });
    for (var k in hashdata) {
        if (hashdata.hasOwnProperty(k)) {
            var key = parseFloat((k - step/2).toFixed(2));
            results.push({'x':key, 'y':median(hashdata[k])});
        }
    }
    return results;
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


function median(ary) {
    var numA, i;
    for (i = ary.length-1; i >= 0; i--) {
        if (ary[i] !== +ary[i]) ary[i] = Number.NEGATIVE_INFINITY;
    }
    numA = function(a, b){return (a-b);};
    ary.sort(numA);
    while (ary.length > 1 && !isFinite(ary[0])) ary.shift();
    return ary[Math.floor(ary.length/2)];
}

function filterbytype(d) {
    if (filtertype == 'all') { return true; }
    var r = d.region;
    if (r==filtertype) { return true; }
    if ((filtertype == 'ca') && ((r == 'sc' || r == 'nc'))) {
        return true;
    }
//    console.log('Bad ' + r + ' vs ' + filtertype);
    return false;
}

function drawConfidence(svg,conf,rawdata,floor) {
    var confdata = getconf(svg,conf/100,rawdata,floor);

    var line = d3.svg.line()
        .x(function(d,i) {
            var x = d.x;
            if (x < svg.xmin) { x = svg.xmin; }
            return svg.x_scale(x);
        })
        .y(function(d) { 
            return svg.y_scale(d.y); 
        })
    svg.append('path')
        .attr('d',line(confdata))
        .attr('class','path conf')
        .attr('id','path_conf_' + conf);
}

function getconf(svg,conf,data,floor) {
    var hashdata = {};
    var keys = [];
    var results = [];
    var step = parseFloat(svg.medianstep);
    $.each(data,function(i,d){
        var x = d.x, y=d.y;
        if ((y>svg.ymax) || (y<svg.ymin)) { return; }
        for (a=svg.xmin; a<svg.xmax; a = parseFloat((a+step).toFixed(2))) {
            if (x >= a+step/2) { continue; }
            var index = a.toString();
            if (hashdata.hasOwnProperty(index)) {
                hashdata[index].push(y);
            }
            else {
                keys.push(index);
                hashdata[index] = [ y ];
            }
            break;
       }
    });

    console.log('Got indices:');
    keys.sort(function(a,b){return(parseFloat(a)-parseFloat(b))});
    console.log(keys);
    console.log(hashdata);    
    for (var i=0; i<keys.length; i++) {
        var k = keys[i];
            console.log('Printing ' + k);
        if (hashdata.hasOwnProperty(parseFloat(k))) {
            console.log('Printing ' + k);
            k = parseFloat(k);
            vals = hashdata[k].sort(function(a,b){return (a-b)});
            if (floor) {
                vals = vals.reverse();
                console.log('vals is now');
                console.log(vals);
            }
            var key = parseFloat((k - step/2 - 1).toFixed(2));
            var key2 = parseFloat((k + step/2 - 1).toFixed(2));
            var hlen = hashdata[k].length;
            var kconf = parseInt(hlen * conf);
            if (floor) { 
                console.log('val=' + vals[kconf]);
                kconf += 1; 
                console.log('val=' + vals[kconf]);
            }
            var val = vals[kconf];   
            console.log(key + '-' + key2 + ' : ' + kconf + '/' + hlen)
            results.push({'x':key, 'y':val});
            results.push({'x':key2, 'y':val});
        }
    }
    return results;
}

