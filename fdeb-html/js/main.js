import {drawedge} from "./edge.js";

$(function () {
    let asrank = []
    let svg;
    let nnodes = [];
    const width = 1900;
    const height = 1000;

    d3.csv("./data/rank.csv").then(rank => {
        const startTime = performance.now();

        let svg = d3.select('#as_core').append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'svg');


        let map_xy = {}
        rank.forEach(d => {
            if (d.country == "CN" || d.country == 'HK' || d.country == 'TW' || d.country == 'US') {
                let x1 = +d.x
                let y1 = +d.y
                map_xy[`${x1.toFixed(2).padStart(6, '0')},${y1.toFixed(2).padStart(6, '0')}`] = d.country
            }
        })


        //标签美化
        const astip = d3.tip()
            .attr('class', 'AsPoint-tip').html(function (d) {
                return `<div>Country: ${d.country}</div><div>ID: ${d.id}</div>`;
            });
        svg.call(astip);

        const nodeGroup = svg.append('g').attr('class', 'node-group');

        // 绘制节点
        nodeGroup.selectAll('.node')
            .data(rank)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("r", 1) // 设置散点的半径
            .attr("fill",'black') // 设置散点的颜色
            .attr("stroke", "black") // 设置边框颜色为黑色
            .attr("stroke-width", 0.3) // 设置边框宽度为1像素
            .on('click', d => {
                console.log(d)
            })
            .on('mouseover', function (d) {
                astip.show(d)
            })
            .on('mouseout', function (d) {
                astip.hide(d)
            });

        drawedge(svg, width, height);


        let lineGenerator = d3.line()
            .x(d => d.x)
            .y(d => d.y)
            .curve(d3.curveLinear);

        const lineGroup = svg.append('g').attr('class', 'line-group');
        const lineGroup1 = lineGroup.append('g').attr('class', 'line-group1');
        const lineGroup2 = lineGroup.append('g').attr('class', 'line-group2');
        const lineGroup3 = lineGroup.append('g').attr('class', 'line-group3');

        nodeGroup.raise();
        d3.json('./data/FDEB.json').then(d => {
            d.forEach((d, i) => {
                let x1 = +d[0].x
                let y1 = +d[0].y

                if (map_xy[`${x1.toFixed(2).padStart(6, '0')},${y1.toFixed(2).padStart(6, '0')}`] == 'CN' || map_xy[`${x1.toFixed(2).padStart(6, '0')},${y1.toFixed(2).padStart(6, '0')}`] == 'HK' || map_xy[`${x1.toFixed(2).padStart(6, '0')},${y1.toFixed(2).padStart(6, '0')}`] == 'TW') {
                    lineGroup1.append("path").attr("d", lineGenerator(d))
                        .style("stroke-width", 0.3)
                        .style("stroke", "red")
                        .style("fill", "none")
                        .style('stroke-opacity', 0.5)
                        .style("pointer-events", "none");
                } else if (map_xy[`${x1.toFixed(2).padStart(6, '0')},${y1.toFixed(2).padStart(6, '0')}`] == 'US') {
                    lineGroup2.append("path").attr("d", lineGenerator(d))
                        .style("stroke-width", 0.3)
                        .style("stroke", "red")
                        .style("fill", "none")
                        .style('stroke-opacity', 0.5)
                        .style("pointer-events", "none");

                } else {
                    lineGroup3.append("path").attr("d", lineGenerator(d))
                        .style("stroke-width", 0.3)
                        .style("stroke", "red")
                        .style("fill", "none")
                        .style('stroke-opacity', 0.5)
                        .style("pointer-events", "none");
                }


            })

        }).catch(error => {
            console.log('存储的文件不存在')
            //预存储文件不存在，计算并下载数据
            d3.json("./data/nnodes.json").then(function (nnodes1) {
                nnodes = nnodes1
                return d3.json("./data/eedges.json")
            }).then(function (eedges) {
                //FDEB
                let fbundling = d3.GPUForceEdgeBundling().nodes(nnodes).edges(eedges)
                let results = fbundling();
                //文件导出和读取
                const data = JSON.stringify(results);
                const blob = new Blob([data], {type: 'application/json'});
                const href = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = href;
                link.download = "FDEB.json";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(href);
                //绘制
                for (var i = 0; i < results.length; i++) {
                    svg.append("path").attr("d", lineGenerator(results[i]))
                        .style("stroke-width", 1)
                        .style("stroke", "#ff2222")
                        .style("fill", "none")
                        .style('stroke-opacity', 0.01)
                }

                const endTime = performance.now()
                console.log(`loaded time ${(endTime - startTime).toFixed(2)} milliseconds`)
            })
        })
        lineGroup2.raise();
        lineGroup1.raise();

    })
})
