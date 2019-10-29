class lineChart {

    constructor(opts) {
        // load in arguments from config object
        this.data = opts.data;
        this.element = opts.element;
        this.xax = opts.xax;
        this.yax = opts.yax;
        // create the chart
        this.draw();
    }

    draw() {
        // define width, height and margin
        this.width = this.element.offsetWidth;
        this.height = this.width / 2;
        this.margin = {
            top: 20,
            right: 75,
            bottom: 45,
            left: 50
        };

        // set up parent element and SVG
        this.element.innerHTML = '';
        const svg = d3.select(this.element).append('svg');
        svg.attr('width', this.width);
        svg.attr('height', this.height);

        // we'll actually be appending to a <g> element
        this.plot = svg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

        // // create the other stuff
        // this.createScales();
        // this.addAxes();
        // this.addLine();
    }

    createScales() {
        // shorthand to save typing later
        const m = this.margin;

        // calculate max and min for data
        const xExtent = d3.extent(this.data, d => d[this.xax]);
        const yExtent = d3.extent(this.data, d => d[this.yax]);

        // force zero baseline if all data points are positive
        if (yExtent[0] > 0) { yExtent[0] = 0; };

        if (this.xax == 'timestamp') {
            this.xScale = d3.scaleTime()
        } else {
            this.xScale = d3.scaleLinear()
        }
        this.xScale.range([0, this.width - m.right])
            .domain(xExtent);

        this.yScale = d3.scaleLinear()
            .range([this.height - (m.top + m.bottom), 0])
            .domain(yExtent);
    }

    addAxes() {
        const m = this.margin;

        // create and append axis elements
        // this is all pretty straightforward D3 stuff
        const xAxis = d3.axisBottom()
            .scale(this.xScale)
        if (this.xax == 'timestamp') {
            xAxis.tickFormat(d3.timeFormat("%b-%d %H:%M"));
        }

        const yAxis = d3.axisLeft()
            .scale(this.yScale);
        if (this.xax == 'timestamp') {
            this.plot.append("g")
                .attr("class", "x axis")
                .attr("transform", `translate(0, ${this.height - (m.top + m.bottom)})`)
                .call(xAxis)
                .selectAll("text")
                .attr("transform", "translate(-10, 10) rotate(20)")
                .style("text-anchor", "start");
        } else {
            this.plot.append("g")
                .attr("class", "x axis")
                .attr("transform", `translate(0, ${this.height - (m.top + m.bottom)})`)
                .call(xAxis)
        }

        this.plot.append("g")
            .attr("class", "y axis")
            .call(yAxis)
    }

    addLine(xax, yax, lineId) {
        this.xax = xax;
        this.yax = yax;
        let line = d3.line()
            .x(d => this.xScale(d[this.xax]))
            .y(d => this.yScale(d[this.yax]));

        console.log(this.lineId)
        console.log(this.xax)
        console.log(this.yax)
        this.plot.append('path')
            // use data stored in `this`
            .datum(this.data)
            .attr("id", lineId)
            .classed('line', true)
            .attr('d', line)
            // set stroke to specified color, or default to red
            .style('stroke', this.lineColor || 'red');
    }

    // the following are "public methods"
    // which can be used by code outside of this file

    setColor(lineId, newColor) {
        // this.plot.select('.line')
        //     .style('stroke', newColor);

        this.plot.select("#"+lineId)
            .style('stroke', newColor);

        // store for use when redrawing
        this.lineColor = newColor;
    }

    setData(newData) {
        this.data = newData;

        // full redraw needed
        this.draw();
    }
}
