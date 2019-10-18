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

        // Draw timeline
        drawLine(data);

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
            .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
            .attr("r", s)
            .style("fill", d => colorScale(d.ax))
            .attr("stroke", "none")
            .attr("stroke-width", 0)
            .attr("fill-opacity", .4)
    }

    // Function that update circle position if something change
    function updateCircles(baseMap) {
        d3.selectAll("circle")
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

    function drawLine(data) {
        let body = d3.select("#acc-g")
        let bodyWidth = 840
        let bodyHeight = 440

        let xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.timestamp))
            .range([0, bodyWidth])
        let yScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.axs))
            .range([bodyHeight, 0])

        let valueLine = d3.line()
            .x(d => xScale(d.timestamp))
            .y(d => yScale(d.axs))
        body.append("path")
            .datum(data)
            .attr("d", valueLine)
            .attr("class", "line")
            .attr("stroke", "orange")

        body.append("g")
            .style("font", "18px times")
            .attr("transform", "translate(0," + bodyHeight + ")")
            .call(d3.axisBottom(xScale)
                .tickFormat(d3.timeFormat("%b-%d %H:%M:%S"))
            )
            .selectAll("text")
            .attr("y", 0)
            .attr("x", 9)
            .attr("dy", ".35em")
            .attr("transform", "translate(-10, 10) rotate(20)")
            .style("text-anchor", "start");

        body.append("g")
            .style("font", "18px times")
            .attr("transform", "translate(0,0)")
            .call(d3.axisLeft(yScale))


    }

    Promise.all([d3.csv("all_data.csv")]).then(showData);