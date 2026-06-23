// charts.js - Chart rendering with spec filtering and time range support

const ChartRenderer = {
    charts: {},
    colors: ['#2563eb', '#059669', '#dc2626', '#7c3aed', '#ea580c', '#0891b2', '#db2777', '#64748b'],

    commonOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: {
                position: 'top', align: 'end',
                labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 12, family: "'Segoe UI', sans-serif" } }
            },
            tooltip: {
                backgroundColor: 'rgba(255,255,255,0.96)',
                titleColor: '#1a1a2e', bodyColor: '#4a4a6a',
                borderColor: '#e8e8f0', borderWidth: 1,
                padding: 12, cornerRadius: 8,
                displayColors: true, boxPadding: 4
            }
        },
        scales: {
            x: {
                grid: { display: false, drawBorder: false },
                ticks: { color: '#8a8a9a', font: { size: 11 }, maxTicksLimit: 10 }
            },
            y: {
                grid: { color: '#f0f0f5', drawBorder: false },
                ticks: { color: '#8a8a9a', font: { size: 11 } }
            }
        },
        elements: {
            point: { radius: 0, hoverRadius: 5, hitRadius: 10 }
        }
    },

    // ---- helpers ----
    filterHistoryByDays(history, days) {
        if (!days || days === 'all' || days === 'ALL') return history;
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - parseInt(days));
        return history.filter(h => new Date(h.date || h.quarter) >= cutoff);
    },

    filterSpecsByType(specs, filterType, data) {
        if (!filterType || filterType === 'all') return specs;
        if (filterType === 'die' && data.specs_die) return data.specs_die;
        if (filterType === 'module' && data.specs_module) return data.specs_module;
        if (filterType === 'ddr5' && data.specs_ddr5) return data.specs_ddr5;
        if (filterType === 'ddr4' && data.specs_ddr4) return data.specs_ddr4;
        if (filterType === 'dimm' && data.specs_dimm) return data.specs_dimm;
        if (filterType === 'pc' && data.specs_pc) return data.specs_pc;
        if (filterType === 'server' && data.specs_server) return data.specs_server;
        if (filterType === 'emmc' && data.specs_emmc) return data.specs_emmc;
        if (filterType === 'ssd' && data.specs_ssd) return data.specs_ssd;
        return specs;
    },

    // ---- spot / daily charts ----
    renderSpotChart(canvasId, data, opts = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const days = opts.days || 'all';
        const filterType = opts.filter || 'all';
        const history = this.filterHistoryByDays(data.history, days);
        const specs = this.filterSpecsByType(data.specs, filterType, data);

        const datasets = specs.map((spec, idx) => ({
            label: spec,
            data: history.map(h => ({ x: h.date, y: h[spec] })),
            borderColor: this.colors[idx % this.colors.length],
            backgroundColor: this.colors[idx % this.colors.length] + '18',
            borderWidth: 2, tension: 0.3, fill: false
        }));

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.plugins.tooltip.callbacks = {
            title: (items) => {
                const item = items[0];
                return item ? item.label : '';
            },
            label: (ctx) => {
                let label = ctx.dataset.label || '';
                if (label) label += ': ';
                if (ctx.parsed.y !== null) {
                    label += ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 3 }) + ' USD';
                }
                return label;
            }
        };

        // For large datasets, limit ticks
        if (history.length > 200) {
            options.scales.x.ticks.maxTicksLimit = 6;
        }

        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        this.charts[canvasId] = new Chart(ctx, { type: 'line', data: { datasets }, options });
    },

    // ---- contract / quarterly charts ----
    renderContractChart(canvasId, data, opts = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const filterType = opts.filter || 'all';
        const specs = this.filterSpecsByType(data.specs, filterType, data);

        const datasets = specs.map((spec, idx) => ({
            label: spec,
            data: data.history.map(h => ({ x: h.date || h.quarter, y: h[spec] })),
            borderColor: this.colors[idx % this.colors.length],
            backgroundColor: this.colors[idx % this.colors.length] + '40',
            borderWidth: 2, pointRadius: 4, pointHoverRadius: 6,
            tension: 0.2, fill: false
        }));

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.scales.x.type = 'category';
        options.plugins.tooltip.callbacks = {
            label: (ctx) => {
                let label = ctx.dataset.label || '';
                if (label) label += ': ';
                if (ctx.parsed.y !== null) label += ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2 }) + ' USD';
                return label;
            }
        };

        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        this.charts[canvasId] = new Chart(ctx, { type: 'line', data: { datasets }, options });
    },

    // ---- stock charts ----
    renderStockChart(canvasId, stockData, color) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !stockData.history || stockData.history.length === 0) return;

        const history = stockData.history;
        const lineColor = color || (stockData.change_pct >= 0 ? '#059669' : '#dc2626');

        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 360);
        gradient.addColorStop(0, lineColor + '30');
        gradient.addColorStop(1, lineColor + '05');

        const currency = stockData.ticker.endsWith('.KS') ? 'KRW' : 'USD';
        const datasets = [{
            label: stockData.name,
            data: history.map(h => ({ x: h.date, y: h.close })),
            borderColor: lineColor, backgroundColor: gradient,
            borderWidth: 2, tension: 0.3, fill: true
        }];

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.plugins.tooltip.callbacks = {
            label: (ctx) => {
                let label = ctx.dataset.label || '';
                if (label) label += ': ';
                if (ctx.parsed.y !== null) label += ctx.parsed.y.toLocaleString() + ' ' + currency;
                return label;
            }
        };

        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        this.charts[canvasId] = new Chart(ctx, { type: 'line', data: { datasets }, options });
    },

    // ---- overview charts (last 6 months only) ----
    renderOverviewChart(canvasId, data, opts = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !data.history || data.history.length === 0) return;

        const filterType = opts.filter || 'all';
        const history = this.filterHistoryByDays(data.history, 180); // 6 months
        const specs = this.filterSpecsByType(data.specs, filterType, data);
        // Only show first 2 specs in overview to keep it clean
        const showSpecs = specs.slice(0, 2);

        const datasets = showSpecs.map((spec, idx) => ({
            label: spec,
            data: history.map(h => ({ x: h.date, y: h[spec] })),
            borderColor: this.colors[idx % this.colors.length],
            borderWidth: 2, tension: 0.3, fill: false
        }));

        const options = JSON.parse(JSON.stringify(this.commonOptions));
        options.plugins.legend.display = false;
        options.plugins.tooltip.callbacks = {
            label: (ctx) => {
                let label = ctx.dataset.label || '';
                if (label) label += ': ';
                if (ctx.parsed.y !== null) label += ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2 }) + ' USD';
                return label;
            }
        };

        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        this.charts[canvasId] = new Chart(ctx, { type: 'line', data: { datasets }, options });
    },

    destroyAll() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
};
