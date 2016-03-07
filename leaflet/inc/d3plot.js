       var svg;
        var selected;
        // Plot functions

        var margin = 50,
            width = 700,
            height = 250;

        function drawGraph() {
            console.log('Now in drawGraph.');

            // Take out epicenter point
            var data = [];
            for (i = 0; i < solutionsData.features.length; i++) {
                pt = solutionsData.features[i];
                if(pt.properties.is_epicenter) {
                    continue;
                }
                data.push(pt);
            }

            if (svg) {
                svg.remove();
            }
            svg = d3.select('#graph')
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            svg.selectAll('circle.resid')
                .data(data).enter()
                .append('circle').attr('class','resid');
            svg.selectAll('circle.npts')
                .data(data).enter()
                .append('circle').attr('class','npts');


            var x_extent = [0,d3.max(data,function(d){
                  return d.properties.t})];
            var y_extent1 = [0,d3.max(data,function(d){
                  return d.properties.resid})];
            var y_extent2 = [0,d3.max(data,function(d){
                  return d.properties.npts})];

            var x_scale = d3.scale.linear().range([margin,width-margin])
                .domain(x_extent);
            var y_scale1 = d3.scale.linear().range([height-margin,margin])
                .domain(y_extent1);
            var y_scale2 = d3.scale.linear().range([height-margin,margin])
                .domain(y_extent2);

            var x_axis = d3.svg.axis().scale(x_scale);
            var y_axis1 = d3.svg.axis().scale(y_scale1).orient('left');
            var y_axis2 = d3.svg.axis().scale(y_scale2).orient('right');

            var line_resid = d3.svg.line()
                .x(function(d){return x_scale(d.properties.t)})
                .y(function(d){return y_scale1(d.properties.resid)});
            var line_npts = d3.svg.line()
                .x(function(d){return x_scale(d.properties.t)})
                .y(function(d){return y_scale2(d.properties.npts)});

            svg.append('path')
                .attr('d',line_resid(data))
                .attr('class','path resid');

            svg.append('path')
                .attr('d',line_npts(data))
                .attr('class','path npts');

            svg.selectAll('circle')
                .attr('cx',function(d){return x_scale(d.properties.t)})
                .on('mouseover',mouseOverGraph);
            svg.selectAll('circle.resid')
                .attr('id',function(d){return 'graph_resid_' + d.properties.t})
                .attr('cy',function(d){return y_scale1(d.properties.resid)});
            svg.selectAll('circle.npts')
                .attr('id',function(d){return 'graph_npts_' + d.properties.t})
                .attr('cy',function(d){return y_scale2(d.properties.npts)});
            svg.selectAll('circle')
                .attr('r',5)
                .call(loadGraphPt);

            svg.append('g')
                .attr('class','x axis')
                .attr('transform','translate(0,'+(height-margin)+')')
                .call(x_axis).append('text')
                .text('Time after origin (s)')
                .attr('x',(width/2)-margin)
                .attr('y',margin/1.5);
            svg.append('g')
                .attr('class','y axis')
                .attr('transform','translate('+margin+',0)')
                .call(y_axis1).append('text')
                .text('Residual')
                .attr('transform','rotate(-90,-32,0) translate(-180)');
            svg.append('g')
                .attr('class','y axis')
                .attr('transform','translate('+(width-margin)+',0)')
                .call(y_axis2).append('text')
                .text('Number of responses')
                .attr('transform','rotate(90,-10,0) translate(55)');

            console.log('Now done with drawGraph.');
        }

    function mouseOverGraph(e) {
        mappt = mappoints[e.properties.t];
        if (mappt) {
            mouseOver(mappt);
        }
    }
    
    function loadGraphPt(e) {
        console.log(e);
        pts = e[0];
        for (i=0; i<pts.length; ++i) {
            t = pts[i].time;
//            graphpoints[t] = pts[i];
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
        console.log(selection);
        selection.style({'stroke':'red','stroke-width':3}).attr('r',8);
        selected = selection;
    }
