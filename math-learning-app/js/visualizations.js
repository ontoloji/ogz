/**
 * Görsel Açıklamalar ve Animasyonlar
 * Matematik kavramlarını görselleştirme
 */

const Visualizations = {
    /**
     * Görselleştirme oluştur
     */
    create(container, type, data) {
        container.innerHTML = '';

        switch (type) {
            case 'fractionCircles':
                this.drawFractionCircles(container, data);
                break;
            case 'fractionRectangles':
                this.drawFractionRectangles(container, data);
                break;
            case 'percentageBar':
                this.drawPercentageBar(container, data);
                break;
            case 'rectangle':
                this.drawRectangle(container, data);
                break;
            case 'square':
                this.drawSquare(container, data);
                break;
            case 'triangle':
                this.drawTriangle(container, data);
                break;
            case 'circle':
                this.drawCircle(container, data);
                break;
            case 'numberLine':
                this.drawNumberLine(container, data);
                break;
            case 'balance':
                this.drawBalance(container, data);
                break;
            case 'barChart':
                this.drawBarChart(container, data);
                break;
            default:
                container.innerHTML = '<p>Görselleştirme yükleniyor...</p>';
        }
    },

    /**
     * SVG container oluştur
     */
    createSVG(width, height) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        return svg;
    },

    /**
     * Kesir daireleri çiz
     */
    drawFractionCircles(container, data) {
        const { fraction1, fraction2 } = data;
        const svg = this.createSVG(400, 150);

        // İlk kesir
        this.drawPieChart(svg, 50, 75, 60, fraction1.num, fraction1.den, '#6366F1');
        const text1 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text1.setAttribute('x', 50);
        text1.setAttribute('y', 145);
        text1.setAttribute('text-anchor', 'middle');
        text1.setAttribute('font-size', '16');
        text1.textContent = `${fraction1.num}/${fraction1.den}`;
        svg.appendChild(text1);

        // Artı işareti
        const plus = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        plus.setAttribute('x', 150);
        plus.setAttribute('y', 80);
        plus.setAttribute('text-anchor', 'middle');
        plus.setAttribute('font-size', '32');
        plus.textContent = '+';
        svg.appendChild(plus);

        // İkinci kesir
        this.drawPieChart(svg, 250, 75, 60, fraction2.num, fraction2.den, '#EC4899');
        const text2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text2.setAttribute('x', 250);
        text2.setAttribute('y', 145);
        text2.setAttribute('text-anchor', 'middle');
        text2.setAttribute('font-size', '16');
        text2.textContent = `${fraction2.num}/${fraction2.den}`;
        svg.appendChild(text2);

        container.appendChild(svg);
    },

    /**
     * Pasta grafik çiz (kesir gösterimi için)
     */
    drawPieChart(svg, cx, cy, r, numerator, denominator, color) {
        // Daire tabanı
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', r);
        circle.setAttribute('fill', '#E2E8F0');
        circle.setAttribute('stroke', '#94A3B8');
        circle.setAttribute('stroke-width', '2');
        svg.appendChild(circle);

        // Dolu parçalar
        const anglePerPart = (2 * Math.PI) / denominator;
        for (let i = 0; i < numerator; i++) {
            const startAngle = i * anglePerPart - Math.PI / 2;
            const endAngle = (i + 1) * anglePerPart - Math.PI / 2;

            const x1 = cx + r * Math.cos(startAngle);
            const y1 = cy + r * Math.sin(startAngle);
            const x2 = cx + r * Math.cos(endAngle);
            const y2 = cy + r * Math.sin(endAngle);

            const largeArc = anglePerPart > Math.PI ? 1 : 0;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
            path.setAttribute('d', d);
            path.setAttribute('fill', color);
            path.setAttribute('opacity', '0.8');
            svg.appendChild(path);
        }

        // Bölüm çizgileri
        for (let i = 0; i < denominator; i++) {
            const angle = i * anglePerPart - Math.PI / 2;
            const x = cx + r * Math.cos(angle);
            const y = cy + r * Math.sin(angle);

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', cx);
            line.setAttribute('y1', cy);
            line.setAttribute('x2', x);
            line.setAttribute('y2', y);
            line.setAttribute('stroke', '#64748B');
            line.setAttribute('stroke-width', '2');
            svg.appendChild(line);
        }
    },

    /**
     * Kesir dikdörtgenleri çiz
     */
    drawFractionRectangles(container, data) {
        const { fraction1, fraction2 } = data;
        const svg = this.createSVG(400, 150);

        // İlk kesir
        this.drawFractionRect(svg, 30, 30, 120, 80, fraction1.num, fraction1.den, '#6366F1');
        const text1 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text1.setAttribute('x', 90);
        text1.setAttribute('y', 130);
        text1.setAttribute('text-anchor', 'middle');
        text1.setAttribute('font-size', '16');
        text1.textContent = `${fraction1.num}/${fraction1.den}`;
        svg.appendChild(text1);

        // Çarpı işareti
        const multiply = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        multiply.setAttribute('x', 200);
        multiply.setAttribute('y', 75);
        multiply.setAttribute('text-anchor', 'middle');
        multiply.setAttribute('font-size', '32');
        multiply.textContent = '×';
        svg.appendChild(multiply);

        // İkinci kesir
        this.drawFractionRect(svg, 250, 30, 120, 80, fraction2.num, fraction2.den, '#EC4899');
        const text2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text2.setAttribute('x', 310);
        text2.setAttribute('y', 130);
        text2.setAttribute('text-anchor', 'middle');
        text2.setAttribute('font-size', '16');
        text2.textContent = `${fraction2.num}/${fraction2.den}`;
        svg.appendChild(text2);

        container.appendChild(svg);
    },

    /**
     * Kesir dikdörtgen çiz
     */
    drawFractionRect(svg, x, y, width, height, numerator, denominator, color) {
        const rectWidth = width / denominator;

        for (let i = 0; i < denominator; i++) {
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x + i * rectWidth);
            rect.setAttribute('y', y);
            rect.setAttribute('width', rectWidth);
            rect.setAttribute('height', height);
            rect.setAttribute('fill', i < numerator ? color : '#E2E8F0');
            rect.setAttribute('stroke', '#64748B');
            rect.setAttribute('stroke-width', '2');
            svg.appendChild(rect);
        }
    },

    /**
     * Yüzde çubuğu çiz
     */
    drawPercentageBar(container, data) {
        const { total, percentage } = data;
        const value = (total * percentage) / 100;

        const div = document.createElement('div');
        div.style.cssText = 'text-align: center; padding: 20px;';

        div.innerHTML = `
            <div style="font-size: 24px; margin-bottom: 20px;">
                ${total} sayısının %${percentage}'i = <strong>${value}</strong>
            </div>
            <div style="width: 100%; height: 60px; background: #E2E8F0; border-radius: 10px; position: relative; overflow: hidden;">
                <div style="width: ${percentage}%; height: 100%; background: linear-gradient(90deg, #6366F1, #EC4899);
                     display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">
                    %${percentage}
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 16px; color: #64748B;">
                ${value} / ${total}
            </div>
        `;

        container.appendChild(div);
    },

    /**
     * Dikdörtgen çiz (geometri)
     */
    drawRectangle(container, data) {
        const { width, height } = data;
        const svg = this.createSVG(300, 250);

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', 50);
        rect.setAttribute('y', 50);
        rect.setAttribute('width', width * 10);
        rect.setAttribute('height', height * 10);
        rect.setAttribute('fill', '#6366F1');
        rect.setAttribute('fill-opacity', '0.3');
        rect.setAttribute('stroke', '#6366F1');
        rect.setAttribute('stroke-width', '3');
        svg.appendChild(rect);

        // Ölçüler
        this.addMeasurement(svg, 50, 40, 50 + width * 10, 40, `${width} cm`);
        this.addMeasurement(svg, 35, 50, 35, 50 + height * 10, `${height} cm`, true);

        container.appendChild(svg);
    },

    /**
     * Kare çiz (geometri)
     */
    drawSquare(container, data) {
        const { side } = data;
        const svg = this.createSVG(300, 250);

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', 75);
        rect.setAttribute('y', 50);
        rect.setAttribute('width', side * 10);
        rect.setAttribute('height', side * 10);
        rect.setAttribute('fill', '#EC4899');
        rect.setAttribute('fill-opacity', '0.3');
        rect.setAttribute('stroke', '#EC4899');
        rect.setAttribute('stroke-width', '3');
        svg.appendChild(rect);

        // Ölçü
        this.addMeasurement(svg, 75, 40, 75 + side * 10, 40, `${side} cm`);

        container.appendChild(svg);
    },

    /**
     * Üçgen çiz (geometri)
     */
    drawTriangle(container, data) {
        const { base, height } = data;
        const svg = this.createSVG(300, 250);

        const points = `50,${200} ${50 + base * 10},200 ${50},${200 - height * 10}`;
        const triangle = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        triangle.setAttribute('points', points);
        triangle.setAttribute('fill', '#10B981');
        triangle.setAttribute('fill-opacity', '0.3');
        triangle.setAttribute('stroke', '#10B981');
        triangle.setAttribute('stroke-width', '3');
        svg.appendChild(triangle);

        // Ölçüler
        this.addMeasurement(svg, 50, 215, 50 + base * 10, 215, `${base} cm`);
        this.addMeasurement(svg, 35, 200, 35, 200 - height * 10, `${height} cm`, true);

        // Yükseklik çizgisi (kesikli)
        const heightLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        heightLine.setAttribute('x1', 50);
        heightLine.setAttribute('y1', 200 - height * 10);
        heightLine.setAttribute('x2', 50);
        heightLine.setAttribute('y2', 200);
        heightLine.setAttribute('stroke', '#10B981');
        heightLine.setAttribute('stroke-width', '2');
        heightLine.setAttribute('stroke-dasharray', '5,5');
        svg.appendChild(heightLine);

        container.appendChild(svg);
    },

    /**
     * Daire çiz (geometri)
     */
    drawCircle(container, data) {
        const { radius } = data;
        const svg = this.createSVG(300, 300);

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', 150);
        circle.setAttribute('cy', 150);
        circle.setAttribute('r', radius * 10);
        circle.setAttribute('fill', '#F59E0B');
        circle.setAttribute('fill-opacity', '0.3');
        circle.setAttribute('stroke', '#F59E0B');
        circle.setAttribute('stroke-width', '3');
        svg.appendChild(circle);

        // Yarıçap çizgisi
        const radiusLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        radiusLine.setAttribute('x1', 150);
        radiusLine.setAttribute('y1', 150);
        radiusLine.setAttribute('x2', 150 + radius * 10);
        radiusLine.setAttribute('y2', 150);
        radiusLine.setAttribute('stroke', '#F59E0B');
        radiusLine.setAttribute('stroke-width', '2');
        svg.appendChild(radiusLine);

        // Merkez noktası
        const center = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        center.setAttribute('cx', 150);
        center.setAttribute('cy', 150);
        center.setAttribute('r', 4);
        center.setAttribute('fill', '#F59E0B');
        svg.appendChild(center);

        // Ölçü
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', 150 + (radius * 10) / 2);
        text.setAttribute('y', 145);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '14');
        text.setAttribute('fill', '#F59E0B');
        text.textContent = `r = ${radius} cm`;
        svg.appendChild(text);

        container.appendChild(svg);
    },

    /**
     * Sayı doğrusu çiz
     */
    drawNumberLine(container, data) {
        const { num1, num2, operation } = data;
        const svg = this.createSVG(600, 150);

        const centerX = 300;
        const centerY = 75;
        const scale = 15;
        const min = Math.min(num1, num2, num1 + num2, 0) - 2;
        const max = Math.max(num1, num2, num1 + num2, 0) + 2;

        // Ana çizgi
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', 50);
        line.setAttribute('y1', centerY);
        line.setAttribute('x2', 550);
        line.setAttribute('y2', centerY);
        line.setAttribute('stroke', '#64748B');
        line.setAttribute('stroke-width', '2');
        svg.appendChild(line);

        // İşaretler
        for (let i = min; i <= max; i++) {
            const x = centerX + i * scale;
            const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            tick.setAttribute('x1', x);
            tick.setAttribute('y1', centerY - 5);
            tick.setAttribute('x2', x);
            tick.setAttribute('y2', centerY + 5);
            tick.setAttribute('stroke', '#64748B');
            tick.setAttribute('stroke-width', '2');
            svg.appendChild(tick);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', centerY + 25);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.textContent = i;
            svg.appendChild(text);
        }

        // İlk sayı
        this.drawPoint(svg, centerX + num1 * scale, centerY - 20, num1.toString(), '#6366F1');

        // İkinci sayı ve sonuç
        if (operation === 'add') {
            const result = num1 + num2;
            this.drawArrow(svg, centerX + num1 * scale, centerY - 20,
                          centerX + result * scale, centerY - 20, '#EC4899');
            this.drawPoint(svg, centerX + result * scale, centerY - 20, result.toString(), '#10B981');
        }

        container.appendChild(svg);
    },

    /**
     * Terazi çiz (denklemler için)
     */
    drawBalance(container, data) {
        const div = document.createElement('div');
        div.style.cssText = 'text-align: center; padding: 30px; font-size: 32px;';
        div.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 30px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #6366F1, #EC4899);
                     color: white; border-radius: 15px; min-width: 150px;">
                    ${data.equation.split('=')[0]}
                </div>
                <div style="font-size: 48px;">⚖️</div>
                <div style="padding: 20px; background: linear-gradient(135deg, #10B981, #3B82F6);
                     color: white; border-radius: 15px; min-width: 150px;">
                    ${data.equation.split('=')[1]}
                </div>
            </div>
        `;
        container.appendChild(div);
    },

    /**
     * Çubuk grafik çiz
     */
    drawBarChart(container, data) {
        const { numbers } = data;
        const svg = this.createSVG(500, 300);
        const maxValue = Math.max(...numbers);
        const barWidth = 400 / numbers.length;
        const padding = 50;

        numbers.forEach((value, index) => {
            const barHeight = (value / maxValue) * 200;
            const x = padding + index * barWidth;
            const y = 250 - barHeight;

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', barWidth - 10);
            rect.setAttribute('height', barHeight);
            rect.setAttribute('fill', '#6366F1');
            rect.setAttribute('opacity', '0.8');
            svg.appendChild(rect);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x + (barWidth - 10) / 2);
            text.setAttribute('y', 270);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12');
            text.textContent = value;
            svg.appendChild(text);
        });

        container.appendChild(svg);
    },

    /**
     * Ölçü ekleme yardımcı fonksiyonu
     */
    addMeasurement(svg, x1, y1, x2, y2, label, vertical = false) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('stroke', '#64748B');
        line.setAttribute('stroke-width', '2');
        svg.appendChild(line);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', (x1 + x2) / 2);
        text.setAttribute('y', vertical ? (y1 + y2) / 2 : y1 - 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '14');
        text.setAttribute('fill', '#64748B');
        if (vertical) {
            text.setAttribute('transform', `rotate(-90, ${(x1 + x2) / 2}, ${(y1 + y2) / 2})`);
        }
        text.textContent = label;
        svg.appendChild(text);
    },

    /**
     * Nokta çiz
     */
    drawPoint(svg, x, y, label, color) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', 6);
        circle.setAttribute('fill', color);
        svg.appendChild(circle);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x);
        text.setAttribute('y', y - 15);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '14');
        text.setAttribute('fill', color);
        text.setAttribute('font-weight', 'bold');
        text.textContent = label;
        svg.appendChild(text);
    },

    /**
     * Ok çiz
     */
    drawArrow(svg, x1, y1, x2, y2, color) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('stroke', color);
        line.setAttribute('stroke-width', '3');
        line.setAttribute('marker-end', 'url(#arrowhead)');
        svg.appendChild(line);

        // Ok başı tanımı
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '5');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3, 0 6');
        polygon.setAttribute('fill', color);
        marker.appendChild(polygon);
        defs.appendChild(marker);
        svg.appendChild(defs);
    }
};

// Global erişim için
window.Visualizations = Visualizations;
