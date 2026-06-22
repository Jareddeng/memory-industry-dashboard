// data-loader.js - Loads all JSON data for the dashboard

const DataLoader = {
    data: {},
    loaded: false,

    async loadAll() {
        try {
            const files = [
                'stock_data.json',
                'dram_spot.json',
                'dram_contract.json',
                'nand_spot.json',
                'nand_contract.json',
                'hbm_tracking.json',
                'capacity_expansion.json',
                'latest_report.json',
                'reports_index.json',
                'metadata.json'
            ];

            const promises = files.map(async (file) => {
                try {
                    const response = await fetch(`data/${file}?t=${Date.now()}`);
                    if (response.ok) {
                        this.data[file.replace('.json', '')] = await response.json();
                    }
                } catch (e) {
                    console.warn(`Failed to load ${file}:`, e);
                }
            });

            await Promise.all(promises);
            this.loaded = true;

            // Update header timestamp
            this.updateHeaderTimestamp();
            return true;
        } catch (e) {
            console.error('Data loading failed:', e);
            return false;
        }
    },

    updateHeaderTimestamp() {
        const badge = document.getElementById('update-badge');
        const timestamp = document.getElementById('last-updated');
        const metadata = this.data.metadata;
        
        if (metadata && metadata.last_updated) {
            badge.textContent = '✅ 数据已同步';
            badge.classList.add('updated');
            timestamp.textContent = `更新于: ${metadata.last_updated}`;
        } else if (this.data.stock_data && this.data.stock_data.last_updated) {
            badge.textContent = '✅ 数据已同步';
            badge.classList.add('updated');
            timestamp.textContent = `更新于: ${this.data.stock_data.last_updated}`;
        }
    },

    getStockData() {
        return this.data.stock_data || { stocks: [] };
    },

    getDramSpotData() {
        return this.data.dram_spot || { specs: [], history: [] };
    },

    getDramContractData() {
        return this.data.dram_contract || { specs: [], history: [] };
    },

    getNandSpotData() {
        return this.data.nand_spot || { specs: [], history: [] };
    },

    getNandContractData() {
        return this.data.nand_contract || { specs: [], history: [] };
    },

    getHbmTracking() {
        return this.data.hbm_tracking || { events: [] };
    },

    getCapacityExpansion() {
        return this.data.capacity_expansion || { companies: [] };
    },

    getLatestReport() {
        return this.data.latest_report || null;
    },

    getReportsIndex() {
        return this.data.reports_index || { reports: [] };
    }
};
