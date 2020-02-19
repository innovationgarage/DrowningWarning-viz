loadData = function () {
    d3.csv("/static/files/processed/map_" + mapid + ".csv")
        .then(showData)
        .catch(function (error) {
            console.log('BLAAAAH', error);
            setTimeout(function () {
                loadData();
            }, 600);
        });
}

loadData();
function showData(dataSource) {
    d3.select("#progress")
        .style("display", "none");
    let data = dataSource.map(d => ({
        timestamp: new Date(d.position_time),
        lat: +d.lat,
        long: +d.long,
        ax: +d.ax,
        ay: +d.ay,
        az: +d.az,
        a: ((d.ax ** 2) + (d.ay ** 2) + (d.az ** 2)) ** (1 / 2),
        gx: +d.gx,
        gy: +d.gy,
        gz: +d.gz,
        g: ((d.gx * 2) + (d.gy * 2) + (d.gz * 2)) ** (1 / 2)
    }));
    drawMapChart(data);
}


function drawMapChart(data) {
    // Initialize the map
    var streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { id: '#mapdiv', attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>' }
    )

    // Initiate base maps   
    var baseLayers = {
        "Streets": streets
    };

    var baseMap = L.map('mapdiv', {
        center: [69.961308, 18.703892],
        zoom: 10,
        layers: baseLayers["Streets"]
    });

    // Initiate overlay maps
    let heatmap_ax = drawHeatmap(data, baseMap, 'ax', 25)
    let heatmap_ay = drawHeatmap(data, baseMap, 'ay', 25)
    let heatmap_az = drawHeatmap(data, baseMap, 'az', 25)
    let heatmap_a = drawHeatmap(data, baseMap, 'Accelaration', 25)
    let heatmap_gx = drawHeatmap(data, baseMap, 'gx', 25)
    let heatmap_gy = drawHeatmap(data, baseMap, 'gy', 25)
    let heatmap_gz = drawHeatmap(data, baseMap, 'gz', 25)
    let heatmap_g = drawHeatmap(data, baseMap, 'Gyro', 25)
    var overlayMaps = {
        "Acceleration": heatmap_a,
        "ax": heatmap_ax,
        "ay": heatmap_ay,
        "az": heatmap_az,
        "Gyro": heatmap_g,
        "gx": heatmap_gx,
        "gy": heatmap_gy,
        "gz": heatmap_gz
    }

    // Add dynamic URL hash for all layers
    var allMapLayers = {
        "Acceleration": heatmap_a,
        "ax": heatmap_ax,
        "ay": heatmap_ay,
        "az": heatmap_az,
        "Gyro": heatmap_g,
        "gx": heatmap_gx,
        "gy": heatmap_gy,
        "gz": heatmap_gz,
        'Streets': baseLayers["Streets"]
    };
    var hash = new L.Hash(baseMap, allMapLayers);

    // Add a controler
    L.control.layers(baseLayers, overlayMaps).addTo(baseMap);
    baseMap.addLayer(heatmap_a);

    let body = d3.select("#mapdiv").select("svg").append("g")
    body.attr("id", "trackgroup")

}

function drawHeatmap(data, baseMap, param, s) {
    let locations = data.map(d => [d.lat, d.long, d[param]])
    let heat = L.heatLayer(locations, { radius: s });
    return heat
}
