// d3magdist.js
var svgmagdist;

function drawMagDist() {
//    var xmin = 2.5, xmax = 6.5, ymin = 0, ymax = 200, medianstep = 0.5;
    var xmin = 1, xmax = 2000, ymin = 0, ymax = 200, medianstep = 100;

var margin = 50,
    width = 500,
    height = 350;
    var svg = svgmagdist;
    console.log('Now in drawMagDist.');
    if (!svg) {
        svg = d3.select('#graphMagDist')
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        svgmagdist = svg;
    }
    else {
        console.log('Removing drawMagDist.');
        svg.selectAll('*').remove();
    }
    svg.xmin = xmin;
    svg.xmax = xmax;
    svg.ymin = ymin;
    svg.ymax = ymax;
    svg.medianstep = medianstep;

    var rawdata = [];
    $.each(alldata,function(i,d){
        if(!filterbytype(d)) { return; }
        rawdata.push({ 'x':d.npts, 'y':d.dist, 'region':d.region});
    });
    svg.selectAll('circle.events')
        .data(rawdata).enter()
        .append('circle').attr('class','events');

    var x_extent = [xmin,xmax];
    var y_extent = [ymin,ymax];

    x_scale = d3.scale.linear().range([margin,width-margin])
        .domain(x_extent);
    y_scale = d3.scale.linear().range([height-margin,margin])
        .domain(y_extent);

    svg.x_scale = x_scale;
    svg.y_scale = y_scale;

    var x_axis = d3.svg.axis().scale(x_scale).ticks(10, "");
    var y_axis = d3.svg.axis().scale(y_scale).orient('left');

    svg.append('g')
        .attr('class','x axis')
        .attr('transform','translate(0,'+(height-margin)+')')
        .call(x_axis).append('text')
        .text('Number of responses')
        .attr('x',(width/2)-margin)
        .attr('y',margin/1.5);
    svg.append('g')
        .attr('class','y axis')
        .attr('transform','translate('+margin+',0)')
        .call(y_axis).append('text')
        .text('Distance to recorded epicenter (km)')
        .attr('transform','rotate(-90,-32,0) translate(-270)');

    svg.selectAll('circle.events')
        .filter(function(d) {
          return true;
//            return ((d.npts >= 100) && (d.dist<=ymax) && (d.dist>=ymin))
        })
        .filter(function(d) { return filterbytype(d)})
        .attr('cx',function(d){return x_scale(d.x)})
        .attr('cy',function(d){return y_scale(d.y)})
        .attr('class',function(d){return ('circle events ' + d.region)})
        .attr('r',5)
        .on('click',function(d){console.log(d)});

    confintervals = [ 50 ];
    for (var i=0; i <confintervals.length; i++) {
        drawConfidenceMag(svg,confintervals[i],rawdata,false);
    }

  function drawConfidenceMag(svg,conf,rawdata,floor) {
      console.log('Rawdata:');
      console.log(rawdata);
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


}
