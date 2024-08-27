document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const nodeInput = document.getElementById('nodeInput');
    const colorInput = document.getElementById('colorInput');
    let nodeData = [];
    let colorMatrix = [];

    fileInput.addEventListener('change', handleFileSelect);
    nodeInput.addEventListener('change', handleNodeFileSelect);
    colorInput.addEventListener('change', handleColorFileSelect);

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const matrix = parseMatrix(e.target.result);
                drawImageFromMatrix(matrix, colorMatrix, nodeData);
            };
            reader.readAsText(file);
        }
    }

    function handleNodeFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                nodeData = parseNodeData(e.target.result);
            };
            reader.readAsText(file);
        }
    }

    function handleColorFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                colorMatrix = parseMatrix(e.target.result);
            };
            reader.readAsText(file);
        }
    }

    function parseMatrix(text) {
        const lines = text.trim().split('\n');
        return lines.map(line => line.trim().split(/\s+/).map(Number));
    }

    function parseNodeData(text) {
        const lines = text.trim().split('\n').slice(1);
        return lines.map(line => {
            const cols = line.split(',');
            const id = cols[0].trim();
            const country = cols[2].trim();
            const grid_x = parseInt(cols[11].trim());
            const grid_y = parseInt(cols[12].trim());
            return {id: id, x: grid_x, y: grid_y, c: country};
        });
    }

function drawImageFromMatrix(matrix, colorMatrix, nodes) {
    let dpi = 800;
    const canvas = document.getElementById('pixelCanvas');
    const ctx = canvas.getContext('2d');
    const imageData = ctx.createImageData(dpi, dpi);

    const useColorMatrix = colorMatrix && colorMatrix.length > 0;

    for (let y = 0; y < dpi; y++) {
        for (let x = 0; x < dpi; x++) {
            const index = (y * dpi + x) * 4;
            const value = matrix[y][x];
            let color;

            if (useColorMatrix) {
                const colorValue = colorMatrix[y][x];

                if (colorValue === -1) {
                    color = { r: 255, g: 255, b: 255 }; // 白色
                } else if (colorValue >= 0 && colorValue <= 3) {
                    color = getColorFromFixedValue(colorValue, value);
                } else {
                    color = { r: 255, g: 255, b: 255 }; // 如果colorValue不在范围内，则设为白色
                }
            } else {
                // 没有提供colorMatrix时，基于数量的颜色映射策略
                color = getColorFromQuantity(value);
            }

            imageData.data[index] = color.r;
            imageData.data[index + 1] = color.g;
            imageData.data[index + 2] = color.b;
            imageData.data[index + 3] = 255;
        }
    }

    ctx.putImageData(imageData, 0, 0);
    drawNodes(ctx, nodes);
}

function getColorFromQuantity(matrixValue) {
    const endColor = {r:159, g:184, b:205}; // 深蓝色（修正了蓝色值）
    const startColor = { r: 255, g: 255, b: 255 }; // 白色

    // 线性插值，根据矩阵值调整颜色的亮度
    const ratio = matrixValue / 255;

    const r = Math.round(startColor.r * (1 - ratio) + endColor.r * ratio);
    const g = Math.round(startColor.g * (1 - ratio) + endColor.g * ratio);
    const b = Math.round(startColor.b * (1 - ratio) + endColor.b * ratio);

    return { r, g, b };
}





//     function getColorFromFixedValue(colorValue, matrixValue) {
// // const baseColors = [
// //     {r:224, g:236, b:208},
// //     {r: 255, g: 219, b:230},
// //     {r:218, g:205, b:241},
// //     {r:172, g:226, b:224}
// // ];
//
// const baseColors = [
//     {r:255, g:0, b:0},
//     {r: 7, g: 255, b:0},
//     {r:0, g:15, b:255},
//     {r:172, g:226, b:224}
// ];
//
//
//         const startColor = {r: 255, g: 255, b: 255}; // 白色
//         const endColor = baseColors[colorValue];
//
//         const ratio = matrixValue / 255;
//
//         const r = Math.round(startColor.r * (1 - ratio) + endColor.r * ratio);
//         const g = Math.round(startColor.g * (1 - ratio) + endColor.g * ratio);
//         const b = Math.round(startColor.b * (1 - ratio) + endColor.b * ratio);
//
//         return {r, g, b};
//     }


    function getColorFromFixedValue(colorValue, matrixValue) {
        // 定义基础颜色
        const baseColors = [
            {r: 255, g: 0, b: 0},   // 红色
            {r: 7, g: 255, b: 0},    // 绿色
            {r: 0, g: 15, b: 255},   // 蓝色
            {r: 172, g: 226, b: 224} // 青色
        ];

        const endColor = baseColors[colorValue];

        // 这里采用指数函数来实现更平滑的颜色过渡
        const ratio = Math.pow(matrixValue / 255, 2);

        const r = Math.round(255 * (1 - ratio) + endColor.r * ratio);
        const g = Math.round(255 * (1 - ratio) + endColor.g * ratio);
        const b = Math.round(255 * (1 - ratio) + endColor.b * ratio);

        return {r, g, b};
    }


    function adjustColorForBrightnessAndSaturation(color, ratio) {
        // 这里我们简单地通过调整颜色的亮度和饱和度来表示密度
        const brightnessFactor = 1 - ratio; // 亮度随着密度的增加而降低
        const saturationFactor = ratio; // 饱和度随着密度的增加而增加

        // 使用 HSL 色彩模型调整亮度和饱和度
        const hsl = rgbToHsl(color.r, color.g, color.b);
        hsl[1] *= saturationFactor; // 调整饱和度
        hsl[2] *= brightnessFactor; // 调整亮度

        const adjustedColor = hslToRgb(hsl[0], hsl[1], hsl[2]);

        return {
            r: Math.round(adjustedColor[0]),
            g: Math.round(adjustedColor[1]),
            b: Math.round(adjustedColor[2])
        };
    }

    function rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r:
                    h = (g - b) / d + (g < b ? 6 : 0);
                    break;
                case g:
                    h = (b - r) / d + 2;
                    break;
                case b:
                    h = (r - g) / d + 4;
                    break;
            }
            h /= 6;
        }

        return [h, s, l];
    }

    function hslToRgb(h, s, l) {
        let r, g, b;

        if (s === 0) {
            r = g = b = l; // achromatic
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1 / 6) return p + (q - p) * 6 * t;
                if (t < 1 / 2) return q;
                if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
                return p;
            }

            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1 / 3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1 / 3);
        }

        return [r * 255, g * 255, b * 255];
    }


    function drawNodes(ctx, nodes) {
        nodes.forEach((node, index) => {
            ctx.beginPath();
            ctx.arc(node.x, node.y, 1, 0, 2 * Math.PI);
            if (node.c === 'CN') {
                ctx.fillStyle = 'green';
            } else if (node.c === 'US') {
                ctx.fillStyle = 'red';
            } else {
                ctx.fillStyle = 'blue';
            }
            ctx.fill();
            ctx.closePath();

            if (index < 150) {
                ctx.fillStyle = 'black';
                ctx.font = '10px Arial';
                ctx.fillText(node.id, node.x + 3, node.y - 3);
            }
        });
    }
});
