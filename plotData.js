    function showData(dataSources) {
        let data = dataSources[0].map(d => ({
            timestamp: new Date(d.position_time),
            lat: +d.lat,
            long: +d.long,
            ax: +d.ax,
            ay: +d.ay,
            az: +d.az,
            gx: +d.gx,
            gy: +d.gy,
            gz: +d.gz,
            axs: +d.ax_savgol,
            ays: +d.ay_savgol,
            azs: +d.az_savgol,
            gxs: +d.gx_savgol,
            gys: +d.gy_savgol,
            gzs: +d.gz_savgol
        }))

        // Initialize the map
        var baseMap = L
            .map('mapdiv')
            .setView([69.961308, 18.703892], 10);

        drawBaseMap().addTo(baseMap);
        // Add a svg layer to the map
        svglayer = L.svg()
        svglayer.addTo(baseMap);

        // Draw poistions + time as a track
        let body = d3.select("#mapdiv").select("svg").append("g")
        body.attr("id", "trackgroup")
        drawTrack(data, baseMap, body);

        drawPositions(data, baseMap, "red", 10);

        let aData = data.map(d => ({
            x: d.axs,
            y: d.ays,
            z: d.azs,
            xvar: d.timestamp
        }))
        drawLine(aData, d3.select("#svg-a"), d3.select("#time-a"), "Acceleration");
        let gData = data.map(d => ({
            x: d.gxs,
            y: d.gys,
            z: d.gzs,
            xvar: d.timestamp
        }))
        drawLine(gData, d3.select("#svg-g"), d3.select("#time-g"), "Gyro");

        // If the user change the map (zoom or drag), I update circle position:
        baseMap.on("moveend", function() { updateCircles(baseMap); });
        baseMap.on("moveend", function() { updateTrack(baseMap); });

    }

    function drawBaseMap() {
        // Add a tile to the map = a background. Comes from OpenStreetmap
        let baseLayer = L.tileLayer(
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
                maxZoom: 16,
            });
        return baseLayer;
    }

    function drawTrack(data, baseMap, body) {
        let bodyWidth = 900
        let bodyHeight = 500

        let colorScale = d3.scaleSequential(d3.interpolatePiYG)
            .domain(d3.extent(data, d => d.ax))

        let trackLine = d3.line()
            .x(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .y(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)

        body.append("path")
            .datum(data)
            .attr("id", "track")
            .attr("d", trackLine)
            .attr("class", "line")
            .attr("stroke", d => colorScale(d.ax))

    }

    function drawPositions(data, baseMap, color, s) {
        let colorScale = d3.scaleSequential(d3.interpolatePiYG)
            .domain(d3.extent(data, d => d.ax))

        d3.select("#mapdiv")
            .select("svg")
            .selectAll("myCircles")
            .data(data)
            .enter()
            .append("circle")
            .attr("class", "positionCircle")
            .transition()
            .duration(2000)
            .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
            .attr("r", s)
            .style("fill", d => colorScale(d.ax))
            .attr("stroke", "none")
            .attr("stroke-width", 0)
            .attr("fill-opacity", .4)
            //.delay(function(i) { return (i * 2) })

    }

    // Function that update circle position if something change
    function updateCircles(baseMap) {
        d3.selectAll("positionCircle")
            .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
    }

    function updateTrack(baseMap) {
        let trackLine = d3.line()
            .x(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .y(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)

        d3.selectAll("#track")
            .attr('d', trackLine)
            .exit().remove()
    }

    function drawLine(data, svg, body, titleYaxis) {
        let bodyWidth = 840
        let bodyHeight = 440

        let parseTime = d3.timeParse("%Y-%M-%D %H:%M")
        let bisectDate = d3.bisector(function(d) {
            return d.xvar;
        }).right;

        let xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.xvar))
            .range([0, bodyWidth])
        let yScale = d3.scaleLinear()
            //.domain(d3.extent(data, d => d.x))
            .domain([0.3, 0.7])
            .range([bodyHeight, 0])

        let valueLineX = d3.line()
            .x(d => xScale(d.xvar))
            .y(d => yScale(d.x))
        body.append("path")
            .datum(data)
            .attr("d", valueLineX)
            .attr("id", "X")
            .attr("class", "line")
            .attr("data-legend", "X")

        let valueLineY = d3.line()
            .x(d => xScale(d.xvar))
            .y(d => yScale(d.y))
        body.append("path")
            .datum(data)
            .attr("d", valueLineY)
            .attr("id", "Y")
            .attr("class", "line")
            .attr("data-legend", "Y")

        let valueLineZ = d3.line()
            .x(d => xScale(d.xvar))
            .y(d => yScale(d.z))
        body.append("path")
            .datum(data)
            .attr("d", valueLineZ)
            .attr("id", "Z")
            .attr("class", "line")
            .attr("data-legend", "Z")

        // X axis
        body.append("g")
            .style("font", "18px times")
            .attr("class", "axis")
            .attr("transform", "translate(0," + bodyHeight + ")")
            .call(d3.axisBottom(xScale)
                .tickFormat(d3.timeFormat("%b-%d %H:%M"))
            )
            .selectAll("text")
            .attr("transform", "translate(-10, 10) rotate(20)")
            .style("text-anchor", "start");

        // Y axis
        body.append("g")
            .style("font", "18px times")
            .attr("class", "axis")
            .attr("transform", "translate(0,0)")
            .call(d3.axisLeft(yScale))

        // text label for the y axis
        body.append("text")
            //            .attr("transform", "rotate(-90)")
            .attr("y", -20)
            .attr("x", (bodyWidth / 2))
            .attr("dy", "1em")
            .style("text-anchor", "right")
            .style("font-size", "34px")
            .text(titleYaxis);

        // Tooltips
        let focus = body.append("g")
            .attr("class", "focus")
            .style("display", "none");

        focus.append("line")
            .attr("class", "x-hover-line hover-line")
            .attr("y1", 0)
            .attr("y2", bodyHeight);

        focus.append("line")
            .attr("class", "y-hover-line hover-line")
            .attr("x1", bodyWidth)
            .attr("x2", bodyWidth);

        focus.append("circle")
            .attr("r", 7.5);

        focus.append("text")
            .attr("x", 15)
            .attr("dy", ".31em");

        svg.append("rect")
            //            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .attr("transform", "translate(50,50)")
            .attr("class", "overlay")
            .attr("width", bodyWidth)
            .attr("height", bodyHeight)
            .on("mouseover", function() { focus.style("display", null); })
            .on("mouseout", function() { focus.style("display", "none"); })
            .on("mousemove", mousemove);

        function mousemove() {

            let x0 = xScale.invert(d3.mouse(this)[0]),
                i = bisectDate(data, x0, 1),
                d0 = data[i - 1],
                d1 = data[i],
                d = x0 - d0.xvar > d1.xvar - x0 ? d1 : d0;

            focus.attr("transform", "translate(" + xScale(d.xvar) + "," + yScale(d.x) + ")");
            focus.select("text").text(function() { return d.x; });
            focus.select(".x-hover-line").attr("y2", bodyHeight - yScale(d.x));
            focus.select(".y-hover-line").attr("x2", bodyWidth + bodyWidth);
        }
    }

    Promise.all([d3.csv("all_data.csv")]).then(showData);