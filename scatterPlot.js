class scatterPlot(){
    constructor(opts) {
        this.data = opts.data;
        this.element = opts.element;
        this.xax = opts.xax;
        this.yax = opts.yax;
        this.rax = opts.rax;
        this.cax = opts.cax;
        this.cmap = opts.colormap;
        let keys = d3.keys(data[0]);
        keys.includes(this.rax) ? this.bubble = true : this.bubble = false;
        this.draw();
    }

    draw() {
        this.width = 1600;
        this.height = 477.5;
        this.margin = {
            top: 20,
            right: 75,
            bottom: 45,
            left: 50
        };

        // set up parent element ans SVG
        const = d3.select(this.element);
        svg.attr("width", this.width);
        svg.attr("height", this.height);

        this.plot = svg.append("g")
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

        this.createScales();
        this.addPoints();
        this.addAxes();
    }

    createScales() {
        const m = this.margin;

        // calculate max and min for data
        const xExtent = d3.extent(this.data, d => d[this.xax]);
        const yExtent = d3.extent(this.data, d => d[this.yax]);
        let this.xmin = xExtent[0]
        this.xmax = xExtent[1]
        this.ymin = yExtent[0]
        this.ymax = yExtent[1]

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

        if (this.bubble)) {
            const rExtent = d3.extent(this.data, d => d[this.rax]);
            let this.rmin = rExtent[0];
            this.rmax = rExtent[1];
            this.rScale = d3.scaleSqrt()
                .domain([this.rmin, this.rmax])
                .range([200000, 1310000000]); //FIXME!
        }

        const unique = (value, index, self) => {
            return self.indexOf(value) === index
        }
        const uniqueCcategories = this.data[this.cax].filter(unique)
        this.cScale = d2.scaleOrdinal()
            .domain(uniqueCcategories)
            .range(this.cmap);
    }
}