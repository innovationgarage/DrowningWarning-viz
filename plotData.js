    let store = {}

    function loadData() {
        return Promise.all([
            d3.csv("capture_scaled.csv"),
            d3.csv("telespor_clean_relevant.csv")
        ]).then(datasets => {
            store.measurements = datasets[0];
            store.telespor = datasets[1];
            return store;
        })
    }

    function showData() {
        //Get position and box measurements data
        let measurements = store.measurements;
        let telespor = store.telespor;

        agData = measurements.map(d => ({
            time: +d.time,
            ax: +d.ax,
            ay: +d.ay,
            az: +d.az,
            gx: +d.gx,
            gy: +d.gy,
            gz: +d.gz
        }))

        // Initialize the map
        var baseMap = L
            .map('mapdiv')
            .setView([69.961308, 18.703892], 10);

        drawBaseMap().addTo(baseMap);
        // Add a svg layer to the map
        L.svg().addTo(baseMap);

        // Draw poistions + time as a track
        let positions = telespor.map(d => ({
            date: new Date(d.position_time),
            lat: +d.lat,
            long: +d.long
        }));
        console.log(positions)

        drawPositions(positions, baseMap, "red", 4);

        let body = d3.select("#mapdiv").select("svg").append("g")
        body.attr("id", "trackgroup")
        drawTrack(positions, baseMap, body);

        // Draw timeline
        drawLine(positions);

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

        valueLine = d3.line()
            .x(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .y(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)

        body.append("path")
            .datum(data)
            .attr("d", valueLine)
            .attr("class", "line")
            .attr("stroke", "cyan")
    }

    function drawPositions(positions, baseMap, color, s) {
        d3.select("#mapdiv")
            .select("svg")
            .selectAll("myCircles")
            .data(positions)
            .enter()
            .append("circle")
            .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
            .attr("r", s)
            .style("fill", color)
            .attr("stroke", color)
            .attr("stroke-width", 3)
            .attr("fill-opacity", .4)
    }

    // Function that update circle position if something change
    function updateCircles(baseMap) {
        d3.selectAll("circle")
            .attr("cx", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .attr("cy", d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)
    }

    function updateTrack(baseMap) {
        valueLine = d3.line()
            .x(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).x)
            .y(d => baseMap.latLngToLayerPoint([+d.lat, +d.long]).y)

        d3.selectAll("path")
            .attr('d', valueLine)
            .exit().remove()
    }

    function drawLine(data) {
        console.log(data)
        let body = d3.select("#acc-g")
        let bodyWidth = 900
        let bodyHeight = 500

        let xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.long))
            .range([0, bodyWidth])
        let yScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.lat))
            .range([bodyHeight, 0])

        body.append("g")
            .attr("transform", "translate(0," + bodyHeight + ")")
            .call(d3.axisBottom(xScale))

        body.append("g")
            .attr("transform", "translate(0,0)")
            .call(d3.axisLeft(yScale))

        valueLine = d3.line()
            .x(d => xScale(d.long))
            .y(d => yScale(d.lat))
        body.append("path")
            .datum(data)
            .attr("d", valueLine)
            .attr("class", "line")
            .attr("stroke", "rgb(112,22,22)")
    }

    loadData().then(showData)