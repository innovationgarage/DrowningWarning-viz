let line_body = d3.select("#acc-svg")
d3.csv("capture_scaled.csv").then(drawLineChart)

function drawLineChart(data) {
    let bodyWidth = 900
    let bodyHeight = 500

    data = data.map(d => ({
        time: +d.time,
        ax: +d.ax,
        ay: +d.ay,
        az: +d.az,
        gx: +d.gx,
        gy: +d.gy,
        gz: +d.gz
    }))

    console.log(d3.extent(data, d => d.gz))
    let yScale = d3.scaleLinear()
        //.domain(d3.extent(data, d => d.gz))
        .domain([0.3, 0.6])
        .range([bodyHeight, 0])
    let xScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.time))
        //            .domain([10000000, 30000000])
        .range([0, bodyWidth])

    line_body.append("g")
        .attr("transform", "translate(0," + bodyHeight + ")")
        .call(d3.axisBottom(xScale))
    line_body.append("g")
        .attr("transform", "translate(0,0)")
        .call(d3.axisLeft(yScale))

    valueLine_gz = d3.line()
        .x(d => xScale(d.time))
        .y(d => yScale(d.gz))
        .defined(d => !!d.gz)
    line_body.append("path")
        .attr("id", "gz")
        .datum(data)
        .attr("d", valueLine_gz)
        .attr("class", "line")
        .attr("stroke", "rgb(112,22,22)")

    valueLine_gx = d3.line()
        .x(d => xScale(d.time))
        .y(d => yScale(d.gx))
        .defined(d => !!d.gx)
    line_body.append("path")
        .attr("id", "gx")
        .datum(data)
        .attr("d", valueLine_gx)
        .attr("class", "line")
        .attr("stroke", "rgb(43,112,22)")

}