// charts.js - Chart rendering using Chart.js

const ChartRenderer = {
    charts: {},

    colors: [
        '#2563eb', '#059669', '#dc2626', '#7c3aed', '#ea580c', '#0891b2', '#db2777'
    ],

    commonOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                position: 'top',
                align: 'end',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 16,
                    font: {
                        size: 12,
                        family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                titleColor: '#1a1a2e',
                bodyColor: '#4a4a6a',
                borderColor: '#e8e8f0',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
                displayColors: true,
                boxPadding: 4,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(3) + ' USD';
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    color: '#8a8a9a',
                    font: { size: 11 },
                    maxTicksLimit: 8
                }
            },
            y: {
                grid: {
                    color: '#f0f0f5',
                    drawBorder: false
                },
                ticks: {
                    color: '#8a8a9a',
                    font: { size: 11 }
                }
            }
        }
    },

    renderDramSpot(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const datasets = data.specs.map((spec, idx) => ({
            label: spec,
            data: data.history.map(h => ({
                x: h.date,
                y: h[spec]
            })),
            borderColor: this.colors[idx % this.colors.length],
            backgroundColor: this.colors[idx % this.colors.length] + '20',
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 5,
            tension: 0.3,
            fill: false
        }));

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: this.commonOptions
        });
    },

    renderDramContract(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const datasets = data.specs.map((spec, idx) => ({
            label: spec,
            data: data.history.map(h => ({
                x: h.quarter,
                y: h[spec]
            })),
            borderColor: this.colors[idx % this.colors.length],
            backgroundColor: this.colors[idx % this.colors.length] + '40',
            borderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.2,
            fill: false
        }));

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.scales.x.type = 'category';
        options.plugins.tooltip.callbacks.label = function(context) {
            let label = context.dataset.label || '';
            if (label) label += ': ';
            if (context.parsed.y !== null) {
                label += context.parsed.y.toFixed(2) + ' USD';
            }
            return label;
        };

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: options
        });
    },

    renderNandSpot(canvasId, data) {
        // Same as DRAM spot but with different data
        this.renderDramSpot(canvasId, data);
    },

    renderNandContract(canvasId, data) {
        this.renderDramContract(canvasId, data);
    },

    renderStockChart(canvasId, stockData, color) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !stockData.history || stockData.history.length === 0) return;

        const history = stockData.history;
        const isPositive = stockData.change_pct >= 0;
        const lineColor = color || (isPositive ? '#059669' : '#dc2626');

        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 360);
        gradient.addColorStop(0, lineColor + '30');
        gradient.addColorStop(1, lineColor + '05');

        const datasets = [{
            label: stockData.name,
            data: history.map(h => ({
                x: h.date,
                y: h.close
            })),
            borderColor: lineColor,
            backgroundColor: gradient,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 5,
            tension: 0.3,
            fill: true
        }];

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        const currency = stockData.ticker.endsWith('.KS') ? 'KRW' : 'USD';
        options.plugins.tooltip.callbacks.label = function(context) {
            let label = context.dataset.label || '';
            if (label) label += ': ';
            if (context.parsed.y !== null) {
                label += context.parsed.y.toLocaleString() + ' ' + currency;
            }
            return label;
        };

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: options
        });
    },

    renderOverviewChart(canvasId, data, specIndices) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const indices = specIndices || [0, 1];
        const selectedSpecs = indices.map(i => data.specs[i]).filter(Boolean);

        const datasets = selectedSpecs.map((spec, idx) => ({
            label: spec,
            data: data.history.map(h => ({
                x: h.date,
                y: h[spec]
            })),
            borderColor: this.colors[idx % this.colors.length],
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            tension: 0.3,
            fill: false
        }));

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.plugins.legend.display = false;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: options
        });
    },

    destroyAll() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
};
