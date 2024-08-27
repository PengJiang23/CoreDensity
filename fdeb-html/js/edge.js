function drawedge(svg, width, height) {

    // 欧洲   西经9°31’到东经66°10’startAngle: -1*-9.517* Math.PI / 180+Math.PI /2, endAngle: -1*66.167*Math.PI / 180+Math.PI /2,
    // 亚洲   169°40′W ~ 26°3′E
    // 北美洲 167°W——52°W

    // 示例数据
    const arcdata1 = [
        {
            startAngle: -1 * -24 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * 26.05 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "red",
            text: "Europe"
        },
        {
            startAngle: -1 * 26.05 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * 190.33 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "green",
            text: "Asia"
        },
        {
            startAngle: -1 * -167 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * -52 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "pink",
            text: "North America"
        },

        // ...更多数据
    ];

    // 大洋洲 东经110°到东经178° 陆地
    // 南美洲 西经81度-西经35度
    // 非洲 17°33′W—51°24′E
    const arcdata2 = [
        {
            startAngle: -1 * 110 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * 178 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "yellow",
            text: "Oceania"
        },
        {
            startAngle: -1 * -81 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * -34 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "purple",
            text: "South America"
        },
        {
            startAngle: -1 * -17.55 * Math.PI / 180 + Math.PI / 2,
            endAngle: -1 * 51.4 * Math.PI / 180 + Math.PI / 2,
            opacity: 0.5,
            color: "orange",
            text: "Africa"
        },

        // ...更多数据
    ];


    // 创建一个圆环生成器
    const arcGenerator = d3.arc()
        .innerRadius(410)
        .outerRadius(420);

    // 创建一个圆环生成器
    const arcGenerator2 = d3.arc()
        .innerRadius(430)
        .outerRadius(440);

    // 绘制圆环
    const arcs = d3.select('.svg').selectAll(".arc")
        .data(arcdata1)
        .enter()
        .append("g")
        .attr("class", "arc")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    arcs.append("path")
        .attr("d", d => arcGenerator(d))
        .attr("fill", d => d.color)
        .attr("opacity", d => d.opacity);

    // 添加文本
    arcs.append("text")
        .attr("transform", d => `translate(${arcGenerator.centroid(d)})`)
        .attr("text-anchor", "middle")
        .text(d => d.text);

    // 绘制圆环
    const arcs2 = d3.select('.svg').selectAll(".arc2")
        .data(arcdata2)
        .enter()
        .append("g")
        .attr("class", "arc2")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    arcs2.append("path")
        .attr("d", d => arcGenerator2(d))
        .attr("fill", d => d.color)
        .attr("opacity", d => d.opacity);

    // 添加文本
    arcs2.append("text")
        .attr("transform", d => `translate(${arcGenerator2.centroid(d)})`)
        .attr("text-anchor", "middle")
        .text(d => d.text);
}

export {drawedge};