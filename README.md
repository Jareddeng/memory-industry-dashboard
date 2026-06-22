# 存储行业可视化看板

> 实时监控存储行业核心数据：DRAM/NAND价格走势、三大厂商股价、HBM4长协谈判、扩产计划与每日深度报告。

🔗 **在线访问**: https://jareddeng.github.io/memory-industry-dashboard/

---

## 📊 功能概览

| 模块 | 内容 | 数据来源 |
|------|------|----------|
| **价格走势** | DRAM现货/合约价格、NAND Flash现货/合约价格（多规格对比） | DRAMeXchange / TrendForce / 脚本模拟 |
| **股价追踪** | SK海力士(000660.KS)、三星电子(005930.KS)、美光科技(MU) | Yahoo Finance |
| **行业跟踪** | HBM4长协谈判时间线、三大厂商存储扩产计划 | 公司公告 / 行业研报 |
| **深度报告** | 每日存储行业深度报告、交易评价、风险提示 | **ClawBot** / 研报分析 |

---

## 🔄 自动更新机制

通过 **GitHub Actions** 定时执行（每天 2 次）：

| 时间 | 说明 |
|------|------|
| **09:00 (UTC+8)** | 盘前更新数据与报告模板 |
| **21:00 (UTC+8)** | 盘后更新数据与报告模板 |

**触发方式**:
- 定时自动触发
- 手动触发: 仓库页面 → Actions → `Update Dashboard Data` → `Run workflow`

---

## 🤖 ClawBot 深度报告接口

ClawBot 可以通过以下方式每日上传深度报告:

### 方式 1: Markdown 报告（推荐）
直接在 `reports/YYYY-MM-DD.md` 文件中写入报告内容，网站会自动渲染。

**模板位置**: `reports/2026-06-22.md`（参考格式）

```markdown
# 存储行业日报 - 2026-06-22

> 来源: ClawBot / 行业研报

## 市场综述
（今日市场总体情况）

## 价格走势分析
（DRAM/NAND价格变化分析）

## 三大厂商动态
- **SK海力士**: ...
- **三星电子**: ...
- **美光科技**: ...

## 今日交易评价
（对当天交易的评价）

## 风险提示
- ...

## 明日展望
```

### 方式 2: JSON 结构化数据
更新 `data/latest_report.json` 文件，看板会读取结构化数据渲染。

### 方式 3: 通过 GitHub Actions 自动化
可以配置额外的 workflow 步骤，调用 ClawBot API 自动生成报告并提交。

---

## 🏗️ 项目架构

```
memory-industry-dashboard/
├── .github/workflows/
│   └── update-dashboard.yml      # GitHub Actions 定时工作流
├── scripts/
│   ├── fetch_stock_data.py       # 抓取股价数据 (Yahoo Finance)
│   ├── fetch_memory_prices.py    # 抓取/生成存储价格数据
│   └── update_report.py          # 生成每日报告模板
├── data/                          # 数据文件 (JSON)
│   ├── stock_data.json           # 股价数据
│   ├── dram_spot.json            # DRAM现货价格
│   ├── dram_contract.json        # DRAM合约价格
│   ├── nand_spot.json            # NAND现货价格
│   ├── nand_contract.json        # NAND合约价格
│   ├── hbm_tracking.json         # HBM4跟踪数据
│   ├── capacity_expansion.json   # 扩产计划
│   ├── latest_report.json        # 最新报告
│   └── reports_index.json        # 报告索引
├── reports/                       # Markdown 报告
│   └── YYYY-MM-DD.md
├── css/style.css                  # 样式
├── js/
│   ├── data-loader.js            # 数据加载
│   ├── charts.js                 # 图表渲染 (Chart.js)
│   └── dashboard.js              # 看板逻辑
├── index.html                     # 主页面
└── config/
    └── charts_config.json         # 图表配置（扩展用）
```

---

## 📈 扩展指南

### 添加新图表

1. 在 `scripts/` 下新建数据抓取脚本，输出 JSON 到 `data/` 目录
2. 在 `index.html` 中预留 `<section>` 容器
3. 在 `js/charts.js` 中添加图表渲染函数
4. 在 `js/dashboard.js` 中绑定渲染逻辑
5. 在 `config/charts_config.json` 中注册新图表配置（可选）

### 添加新数据源

1. 在 `scripts/` 下创建新的 Python 脚本
2. 在 `.github/workflows/update-dashboard.yml` 的 `update-data` job 中添加步骤
3. 确保输出到 `data/` 目录且 JSON 结构一致

### 添加新分析板块

1. 在 `index.html` 的 `<nav>` 和 `<main>` 中增加对应标签和区域
2. 在 `js/dashboard.js` 的 `renderIndustry()` 或新增方法中实现渲染
3. 在对应数据脚本中生成/抓取数据

---

## 📝 免责声明

本看板数据仅供参考，不构成投资建议。存储行业数据来源于第三方公开信息，可能存在延迟或误差。投资有风险，决策需谨慎。

---

## ⚙️ 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JS + [Chart.js](https://www.chartjs.org/)
- **部署**: GitHub Pages
- **自动化**: GitHub Actions + Python
- **数据**: Yahoo Finance (yfinance) + 公开行业数据源

