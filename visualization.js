d3.csv("all_data.csv").then(showData);

function showData(dataSource) {
    let data = dataSource.map(d => ({
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
    }));
    drawMapChart(data);
    drawLineCharts(data);
}

function drawMapChart(data) {
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
    baseMap.on("moveend", function() { updateTrack(baseMap); });    

    // drawPositions(data, baseMap, 10);
    // // If the user change the map (zoom or drag), I update circle position:
    // baseMap.on("moveend", function () { updateCircles(baseMap); });
    
    drawHeatmap(data, baseMap, 25);
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
}

function drawPositions(data, baseMap, s) {
    let colorScale = d3.scaleSequential(d3.interpolatePiYG)
        .domain(d3.extent(data, d => d.ax))

    d3.select("#mapdiv")
        .select("svg")
        .selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "positionCircle")
        .transition()
        .duration(2000)
        //.delay(function(i) { return (i * 2) })  
        .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
        .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
        .attr("r", s)
        .style("fill", d => colorScale(d.ax))
        .attr("stroke", "none")
        .attr("stroke-width", 0)
        .attr("fill-opacity", .4)
}

function drawHeatmap(data, baseMap, s) {
    let locations = data.map(d => [d.lat, d.long, Math.sqrt(Math.pow(d.gxs,2)+Math.pow(d.gys,2)+Math.pow(d.gzs,2))]);
    let heat = L.heatLayer(locations, { radius: s });
    baseMap.addLayer(heat);
}

// Function that update circle position if something change
function updateCircles(baseMap) {
    d3.selectAll("circle.positionCircle")
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

function drawLineCharts(data) {
    // create new chart using Chart constructor
    let opt_acc = {
        element: "svg.chartSVG.acceleration",
        data: data,
        xax: 'timestamp',
        yaxs: ['axs', 'ays', 'azs'],
        lineIds: ['X', 'Y', 'Z']
    };
    const chart_acc = new lineChart(opt_acc);

    let opt_gyr = {
        element: "svg.chartSVG.gyro",
        data: data,
        xax: 'timestamp',
        yaxs: ['gxs', 'gys', 'gzs'],
        lineIds: ['X', 'Y', 'Z']
    };
    const chart_gyr = new lineChart(opt_gyr);
}