class lineChart {

    constructor(opts) {
        // load in arguments from config object
        this.data = opts.data;
        this.element = opts.element;
        this.xax = opts.xax;
        this.yaxs = opts.yaxs;
        this.lineIds = opts.lineIds;
        this.colors = opts.colors;
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

        let idx;
        for (idx = 0; idx < this.yaxs.length; idx++) {
            this.yax = this.yaxs[idx];
            this.lineId = this.lineIds[idx];
            this.createScales();    
        };
        for (idx = 0; idx < this.yaxs.length; idx++) {
                this.yax = this.yaxs[idx];
                this.lineId = this.lineIds[idx];
                this.addLine();
                this.setColor(this.colors[idx]);
        };
        this.addAxes();
    }

    createScales() {
        // shorthand to save typing later
        const m = this.margin;

        // calculate max and min for data
        const xExtent = d3.extent(this.data, d => d[this.xax]);
        const yExtent = d3.extent(this.data, d => d[this.yax]);

        // Choose the axes extents to include all lines
        if (typeof this.xmin === 'undefined') {
            this.xmin = xExtent[0];
            this.xmax = xExtent[1];
        } else {
            if (this.xmin > xExtent[0]) { this.xmin = xExtent[0]; };
            if (this.xmax < xExtent[1]) { this.xmax = xExtent[1]; };
        }
        if (typeof this.ymin === 'undefined') {
            this.ymin = yExtent[0];
            this.ymax = yExtent[1];
        } else {
            if (this.ymin > yExtent[0]) { this.ymin = yExtent[0]; };
            if (this.ymax < yExtent[1]) { this.ymax = yExtent[1]; };
        }

        // force zero baseline if all data points are positive
        if (this.ymin > 0) { this.ymin = 0; };

        if (this.xax == 'timestamp') {
            this.xScale = d3.scaleTime()
        } else {
            this.xScale = d3.scaleLinear()
        }
        this.xScale.range([0, this.width - m.right])
            .domain([this.xmin, this.xmax]);

        this.yScale = d3.scaleLinear()
            .range([this.height - (m.top + m.bottom), 0])
            .domain([this.ymin, this.ymax]);
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
                .transition()
                .duration(2000)
                .call(xAxis)
                .selectAll("text")
                .attr("transform", "translate(-10, 10) rotate(20)")
                .style("text-anchor", "start");
        } else {
            this.plot.append("g")
                .attr("class", "x axis")
                .attr("transform", `translate(0, ${this.height - (m.top + m.bottom)})`)
                .transition()
                .duration(2000)
                .call(xAxis)
        }

        this.plot.append("g")
            .attr("class", "y axis")
            .transition()
            .duration(2000)
            .call(yAxis)

    }

    addLine() {
        let line = d3.line()
            .x(d => this.xScale(d[this.xax]))
            .y(d => this.yScale(d[this.yax]));

        this.plot.append('path')
            // use data stored in `this`
            .datum(this.data)
            .classed('line', true)
            .attr('d', line)
            .attr("id", this.lineId)
            // set stroke to specified color, or default to red
            .style('stroke', this.lineColor || 'red');
    }

    // the following are "public methods"
    // which can be used by code outside of this file

    setColor(newColor) {
        // this.plot.select('.line')
        //     .style('stroke', newColor);

        this.plot.select("#" + this.lineId)
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
