// dashboard.js - Main dashboard logic and UI rendering

const Dashboard = {
    init() {
        this.bindNavigation();
        this.bindEvents();
        this.loadData();
    },

    bindNavigation() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const section = tab.dataset.section;
                this.switchSection(section);
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            });
        });
    },

    bindEvents() {
        // Expansion tabs
        document.querySelectorAll('.exp-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.exp-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.renderExpansion(tab.dataset.company);
            });
        });

        // Report refresh
        const refreshBtn = document.getElementById('refresh-report-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadReport());
        }

        // Report date selector
        const selector = document.getElementById('report-date-selector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadReport(e.target.value);
                }
            });
        }
    },

    switchSection(section) {
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(section).classList.add('active');

        // Render charts for the active section
        if (section === 'overview') {
            this.renderOverviewCharts();
        } else if (section === 'prices') {
            this.renderPriceCharts();
        } else if (section === 'stocks') {
            this.renderStockCharts();
        } else if (section === 'industry') {
            this.renderIndustry();
        } else if (section === 'reports') {
            this.renderReports();
        }
    },

    async loadData() {
        await DataLoader.loadAll();
        this.renderStockCards();
        this.renderOverviewCharts();
        this.renderLatestReportPreview();
    },

    renderStockCards() {
        const container = document.getElementById('stock-cards');
        if (!container) return;

        const stockData = DataLoader.getStockData();
        if (!stockData.stocks || stockData.stocks.length === 0) {
            container.innerHTML = '<p class="placeholder">暂无股价数据</p>';
            return;
        }

        container.innerHTML = stockData.stocks.map(stock => {
            const isPositive = stock.change_pct >= 0;
            const changeClass = isPositive ? 'positive' : 'negative';
            const changeSymbol = isPositive ? '▲' : '▼';
            const currency = stock.ticker.endsWith('.KS') ? 'KRW' : 'USD';

            return `
                <div class="stock-card">
                    <div class="stock-card-header">
                        <span class="stock-card-name">${stock.name}</span>
                        <span class="stock-card-ticker">${stock.ticker}</span>
                    </div>
                    <div class="stock-card-price">${stock.current_price.toLocaleString()} <span style="font-size:14px;font-weight:400;color:var(--text-muted)">${currency}</span></div>
                    <div class="stock-card-change ${changeClass}">
                        <span>${changeSymbol} ${Math.abs(stock.change_pct).toFixed(2)}%</span>
                        <span class="change-amount">${isPositive ? '+' : ''}${stock.change_amount.toLocaleString()} ${currency}</span>
                    </div>
                    <div class="stock-card-meta">
                        <span>52周高: ${stock.high_52w.toLocaleString()}</span>
                        <span>52周低: ${stock.low_52w.toLocaleString()}</span>
                        <span>成交量: ${(stock.volume / 1000000).toFixed(1)}M</span>
                    </div>
                </div>
            `;
        }).join('');
    },

    renderOverviewCharts() {
        const dramSpot = DataLoader.getDramSpotData();
        const nandSpot = DataLoader.getNandSpotData();

        ChartRenderer.renderOverviewChart('overview-dram-spot', dramSpot, [0, 2]);
        ChartRenderer.renderOverviewChart('overview-nand-spot', nandSpot, [0, 1]);
    },

    renderPriceCharts() {
        ChartRenderer.renderDramSpot('dram-spot-chart', DataLoader.getDramSpotData());
        ChartRenderer.renderDramContract('dram-contract-chart', DataLoader.getDramContractData());
        ChartRenderer.renderNandSpot('nand-spot-chart', DataLoader.getNandSpotData());
        ChartRenderer.renderNandContract('nand-contract-chart', DataLoader.getNandContractData());
    },

    renderStockCharts() {
        const stockData = DataLoader.getStockData();
        const stockDetailContainer = document.getElementById('stock-detail-cards');

        if (stockDetailContainer && stockData.stocks) {
            stockDetailContainer.innerHTML = stockData.stocks.map((stock, idx) => {
                const isPositive = stock.change_pct >= 0;
                const changeClass = isPositive ? 'positive' : 'negative';
                const currency = stock.ticker.endsWith('.KS') ? 'KRW' : 'USD';
                const colors = ['#2563eb', '#059669', '#dc2626'];

                return `
                    <div class="stock-detail-card">
                        <h4>${stock.name} <span style="font-weight:400;color:var(--text-muted)">(${stock.ticker})</span></h4>
                        <div class="detail-price" style="color:${colors[idx]}">${stock.current_price.toLocaleString()} <span style="font-size:18px">${currency}</span></div>
                        <div class="detail-change ${changeClass}">${isPositive ? '▲' : '▼'} ${Math.abs(stock.change_pct).toFixed(2)}% (${stock.change_amount >= 0 ? '+' : ''}${stock.change_amount.toLocaleString()} ${currency})</div>
                        <div class="detail-stats">
                            <div class="detail-stat">
                                <span class="detail-stat-label">昨收</span>
                                <span class="detail-stat-value">${stock.previous_close.toLocaleString()}</span>
                            </div>
                            <div class="detail-stat">
                                <span class="detail-stat-label">52周高</span>
                                <span class="detail-stat-value">${stock.high_52w.toLocaleString()}</span>
                            </div>
                            <div class="detail-stat">
                                <span class="detail-stat-label">52周低</span>
                                <span class="detail-stat-value">${stock.low_52w.toLocaleString()}</span>
                            </div>
                            <div class="detail-stat">
                                <span class="detail-stat-label">成交量</span>
                                <span class="detail-stat-value">${(stock.volume / 1000000).toFixed(1)}M</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        if (stockData.stocks) {
            stockData.stocks.forEach((stock, idx) => {
                const canvasIds = ['sk-hynix-chart', 'samsung-chart', 'micron-chart'];
                const colors = ['#2563eb', '#059669', '#dc2626'];
                if (canvasIds[idx]) {
                    ChartRenderer.renderStockChart(canvasIds[idx], stock, colors[idx]);
                }
            });
        }
    },

    renderIndustry() {
        this.renderHbmTimeline();
        this.renderExpansion('sk-hynix');
    },

    renderHbmTimeline() {
        const container = document.getElementById('hbm-timeline');
        if (!container) return;

        const hbmData = DataLoader.getHbmTracking();
        if (!hbmData.events || hbmData.events.length === 0) {
            container.innerHTML = '<p class="placeholder">暂无HBM4谈判数据</p>';
            return;
        }

        container.innerHTML = hbmData.events.map(event => {
            const statusMap = {
                'completed': '已完成',
                'in_progress': '进行中',
                'upcoming': '待开始'
            };

            return `
                <div class="timeline-item">
                    <div class="timeline-dot ${event.status}"></div>
                    <div class="timeline-date">${event.date}</div>
                    <div class="timeline-title">${event.event}</div>
                    <div class="timeline-detail">${event.detail}</div>
                    <span class="timeline-status ${event.status}">${statusMap[event.status] || event.status}</span>
                </div>
            `;
        }).join('');
    },

    renderExpansion(company) {
        const container = document.getElementById('expansion-content');
        if (!container) return;

        const expansionData = DataLoader.getCapacityExpansion();
        if (!expansionData.companies) {
            container.innerHTML = '<p class="placeholder">暂无扩产计划数据</p>';
            return;
        }

        const companyMap = {
            'sk-hynix': 'SK Hynix',
            'samsung': 'Samsung Electronics',
            'micron': 'Micron Technology'
        };

        const companyData = expansionData.companies.find(c => c.name === companyMap[company]);
        if (!companyData) {
            container.innerHTML = '<p class="placeholder">暂无数据</p>';
            return;
        }

        const statusClassMap = {
            '建设中': 'status-construction',
            '规划': 'status-planning',
            '扩产中': 'status-expanding'
        };

        container.innerHTML = companyData.plans.map(plan => `
            <div class="expansion-item">
                <div class="expansion-item-header">
                    <span class="expansion-item-name">${plan.facility}</span>
                    <span class="expansion-item-status ${statusClassMap[plan.status] || 'status-planning'}">${plan.status}</span>
                </div>
                <div class="expansion-item-meta">
                    <span>类型: ${plan.type}</span>
                    <span>投资: ${plan.investment}</span>
                    <span>时间: ${plan.timeline}</span>
                </div>
                <div class="expansion-item-detail">${plan.detail}</div>
            </div>
        `).join('');
    },

    renderLatestReportPreview() {
        const container = document.getElementById('latest-report-content');
        if (!container) return;

        const report = DataLoader.getLatestReport();
        if (!report) {
            container.innerHTML = '<p class="placeholder">暂无报告，等待ClawBot更新...</p>';
            return;
        }

        // Check if report has real content
        const hasContent = report.summary && report.summary.length > 10 && !report.summary.includes('待ClawBot');

        if (!hasContent) {
            container.innerHTML = `
                <p class="placeholder">📅 ${report.date} 的报告已创建，等待ClawBot填写内容...</p>
                <p style="margin-top:8px;font-size:13px;color:var(--text-muted)">
                    ClawBot可以在 reports/${report.date}.md 文件中填写每日深度报告，
                    或在 data/latest_report.json 中更新结构化数据。
                </p>
            `;
        } else {
            container.innerHTML = `
                <p><strong>${report.title}</strong></p>
                <p>${report.summary}</p>
                ${report.risk_alerts && report.risk_alerts.length > 0 ? `
                    <div style="margin-top:12px;">
                        <strong>⚠️ 风险提示:</strong>
                        <ul>${report.risk_alerts.map(r => `<li>${r}</li>`).join('')}</ul>
                    </div>
                ` : ''}
            `;
        }
    },

    renderReports() {
        const index = DataLoader.getReportsIndex();
        const selector = document.getElementById('report-date-selector');
        const list = document.getElementById('report-list');

        if (selector && index.reports) {
            selector.innerHTML = '<option value="">选择日期...</option>' +
                index.reports.map(r => `<option value="${r.date}">${r.date}</option>`).join('');
        }

        if (list && index.reports) {
            list.innerHTML = index.reports.map((r, idx) => `
                <div class="report-list-item ${idx === 0 ? 'active' : ''}" data-date="${r.date}">
                    <span class="report-list-item-date">${r.date}</span>
                    <span class="report-list-item-badge">日报</span>
                </div>
            `).join('');

            // Click to load report
            list.querySelectorAll('.report-list-item').forEach(item => {
                item.addEventListener('click', () => {
                    list.querySelectorAll('.report-list-item').forEach(i => i.classList.remove('active'));
                    item.classList.add('active');
                    this.loadReport(item.dataset.date);
                });
            });
        }

        // Load latest report by default
        if (index.reports && index.reports.length > 0) {
            this.loadReport(index.reports[0].date);
        }
    },

    async loadReport(date) {
        const container = document.getElementById('report-container');
        const status = document.getElementById('report-status');
        if (!container || !status) return;

        const targetDate = date || new Date().toISOString().split('T')[0];
        status.innerHTML = '<div class="loading-spinner"></div> <span>加载报告中...</span>';

        try {
            // Try to load the markdown report
            const response = await fetch(`reports/${targetDate}.md?t=${Date.now()}`);
            if (response.ok) {
                const markdown = await response.text();
                // Simple markdown to HTML conversion
                const html = this.markdownToHtml(markdown);
                container.innerHTML = `<div class="report-content-rendered">${html}</div>`;
            } else {
                // Fallback to JSON
                const report = DataLoader.getLatestReport();
                if (report && report.date === targetDate) {
                    container.innerHTML = this.renderReportHtml(report);
                } else {
                    status.innerHTML = '<p>📭 暂无该日期的报告</p><p style="font-size:13px;margin-top:8px;">ClawBot可以通过更新 reports/ 目录下的 .md 文件来添加报告</p>';
                }
            }
        } catch (e) {
            status.innerHTML = '<p>❌ 加载报告失败</p>';
        }
    },

    renderReportHtml(report) {
        return `
            <div class="report-content-rendered">
                <h2>${report.title || '存储行业日报'}</h2>
                <p><strong>日期:</strong> ${report.date}</p>
                <p><strong>更新时间:</strong> ${report.last_updated}</p>

                <h3>市场综述</h3>
                <p>${report.summary || '暂无内容'}</p>

                <h3>今日交易评价</h3>
                <p>${report.market_assessment || '暂无内容'}</p>

                <h3>风险提示</h3>
                ${report.risk_alerts && report.risk_alerts.length > 0
                    ? `<ul>${report.risk_alerts.map(r => `<li>${r}</li>`).join('')}</ul>`
                    : '<p>暂无</p>'}

                <h3>展望</h3>
                <p>${report.outlook || '暂无内容'}</p>
            </div>
        `;
    },

    markdownToHtml(md) {
        // Simple markdown conversion
        return md
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/^- (.*$)/gim, '<ul><li>$1</li></ul>')
            .replace(/<\/ul>\s*<ul>/g, '')
            .replace(/\n/gim, '<br>');
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});
