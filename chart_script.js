d3.csv("all_data.csv").then(showData);
function showData(dataSource) {
    let formattedData = dataSource.map(d => ({
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
    // create new chart using Chart constructor
    let opt = {
        element: document.querySelector('.chart-container'),
        data: formattedData,
        xax: 'timestamp',
        yax: 'axs'
    };
    const chart = new lineChart(opt);
    chart.draw();
    chart.createScales();
    chart.addAxes();
    chart.addLine(opt.xax, opt.yax, "axs");
    chart.setColor("axs", "green");
    chart.addLine("gxs", 'gys', "gs");
    chart.setColor("gys", "orange");

    // // change line colour on click
    // d3.selectAll('button.color').on('click', function () {
    //     const color = d3.select(this).text().split(' ')[0];
    //     chart.setColor(color);
    // });
    // // change data on click to something randomly-generated
    // d3.selectAll('button.data').on('click', () => {
    //     chart.setData([
    //         [new Date(2016, 0, 1), Math.random() * 100],
    //         [new Date(2016, 1, 1), Math.random() * 100],
    //         [new Date(2016, 2, 1), Math.random() * 100],
    //         [new Date(2016, 3, 1), Math.random() * 100],
    //         [new Date(2016, 4, 1), Math.random() * 100]
    //     ]);
    // });
    // // redraw chart on each resize
    // // in a real-world example, it might be worth ‘throttling’ this
    // // more info: http://sampsonblog.com/749/simple-throttle-function
    // d3.select(window).on('resize', () => chart.draw());
}