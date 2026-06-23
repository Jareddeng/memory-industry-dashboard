"""
Fetch memory industry price data (DRAM, NAND, HBM)

Generates comprehensive daily price data from 2023-01-01 to present.
In production, this should integrate with:
- DRAMeXchange / TrendForce API (paid)
- InSpectrum (paid)
- DigiTimes (paid)
- Yahoo Finance / Investing.com (free for some data)

Data frequency and time range are explicitly labeled in output JSON.
"""
import json
import os
from datetime import datetime, timedelta
import random
import sys

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
START_DATE = datetime(2023, 1, 3)  # First Monday of 2023
END_DATE = datetime.now()
DAILY_DATA_NOTE = "日频数据 (工作日), 2023-01 至 今"
WEEKLY_DATA_NOTE = "周频数据 (周一), 2023-01 至 今"
QUARTERLY_DATA_NOTE = "季度数据, 2021-Q1 至 今"
DATA_SOURCE_NOTE = "模拟数据 (基于行业历史趋势), 待接入真实API"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def is_weekday(d):
    return d.weekday() < 5

def generate_dates_daily(start, end):
    """Generate list of weekday dates from start to end."""
    dates = []
    cur = start
    while cur <= end:
        if is_weekday(cur):
            dates.append(cur)
        cur += timedelta(days=1)
    return dates

def generate_dates_weekly(start, end):
    """Generate list of Monday dates from start to end."""
    dates = []
    cur = start
    if cur.weekday() != 0:
        cur += timedelta(days=(7 - cur.weekday()) % 7)
    while cur <= end:
        dates.append(cur)
        cur += timedelta(weeks=1)
    return dates

def generate_quarters(start_year, start_q, end_year, end_q):
    """Generate quarter labels."""
    quarters = []
    y, q = start_year, start_q
    while (y, q) <= (end_year, end_q):
        quarters.append({"label": f"Q{q} {y}", "year": y, "quarter": q})
        q += 1
        if q > 4:
            q = 1
            y += 1
    return quarters

def random_walk(base, n_steps, drift=0.0002, vol=0.015, min_val=0.1):
    """Generate realistic correlated random walk."""
    prices = [base]
    for _ in range(n_steps - 1):
        change = random.gauss(drift, vol)
        new_price = prices[-1] * (1 + change)
        new_price = max(new_price, min_val)
        prices.append(new_price)
    return prices

# ------------------------------------------------------------------
# DRAM Spot (Daily, 2023-01 to present)
# ------------------------------------------------------------------
def generate_dram_spot():
    """DRAM daily spot prices (die level + module level)."""
    dates = generate_dates_daily(START_DATE, END_DATE)
    n = len(dates)

    # Base prices aligned with historical market trends (2023-2024 cycle)
    # DRAM颗粒 (Die) prices
    specs = {
        "DDR4 8Gb (1GB×8)": {"base": 1.35, "vol": 0.015, "drift": 0.0001},
        "DDR4 16Gb (2GB×8)": {"base": 2.80, "vol": 0.015, "drift": 0.0001},
        "DDR5 8Gb (1GB×8)": {"base": 1.85, "vol": 0.018, "drift": 0.0003},
        "DDR5 16Gb (2GB×8)": {"base": 3.50, "vol": 0.018, "drift": 0.0003},
    }

    # Module prices (derived from die + assembly margin)
    module_specs = {
        "DDR4 8GB PC 模组": {"base": 22.0, "vol": 0.012, "drift": 0.0001},
        "DDR4 16GB PC 模组": {"base": 42.0, "vol": 0.012, "drift": 0.0001},
        "DDR5 8GB PC 模组": {"base": 30.0, "vol": 0.015, "drift": 0.0003},
        "DDR5 16GB PC 模组": {"base": 58.0, "vol": 0.015, "drift": 0.0003},
        "DDR4 8GB×2 套条": {"base": 44.0, "vol": 0.012, "drift": 0.0001},
        "DDR5 8GB×2 套条": {"base": 60.0, "vol": 0.015, "drift": 0.0003},
    }

    all_specs = {**specs, **module_specs}

    # Generate correlated random walks
    random.seed(42)  # Reproducible for demo
    series = {}
    for name, cfg in all_specs.items():
        series[name] = random_walk(cfg["base"], n, cfg["drift"], cfg["vol"])

    # Apply historical market cycle corrections (2023 crash + 2024 recovery)
    # Q1-Q3 2023: prices down ~30% from peak
    # Q4 2023 - Q2 2024: recovery up ~40%
    # Q3 2024 onwards: stabilization with slight uptrend
    for idx, d in enumerate(dates):
        y, m = d.year, d.month
        cycle_factor = 1.0
        if y == 2023 and m <= 6:
            cycle_factor = 0.70 + 0.30 * ((m - 1) / 5)  # 0.70 -> 1.00
        elif y == 2023 and m <= 9:
            cycle_factor = 1.00 + 0.10 * ((m - 7) / 2)  # 1.00 -> 1.10
        elif y == 2023:
            cycle_factor = 1.10 + 0.15 * ((m - 10) / 2)  # 1.10 -> 1.25
        elif y == 2024 and m <= 6:
            cycle_factor = 1.25 + 0.20 * ((m - 1) / 5)  # 1.25 -> 1.45
        elif y == 2024 and m <= 9:
            cycle_factor = 1.45 - 0.10 * ((m - 7) / 2)  # 1.45 -> 1.40
        elif y == 2024:
            cycle_factor = 1.40 - 0.05 * ((m - 10) / 2)  # 1.40 -> 1.38
        elif y == 2025:
            cycle_factor = 1.38 + 0.05 * ((m - 1) / 11)  # slight uptrend
        else:
            cycle_factor = 1.43 + 0.03 * ((m - 1) / 11)

        for name in all_specs:
            # Apply cycle to original random walk, keeping base structure
            base_factor = all_specs[name]["base"]
            deviation = series[name][idx] / base_factor - 1.0
            series[name][idx] = base_factor * (1.0 + deviation * 0.6 + (cycle_factor - 1.0) * 0.4)
            # Add small random noise after cycle correction
            series[name][idx] *= (1 + random.gauss(0, 0.005))
            # Granularity: die prices 3 decimals, module prices 2 decimals
            if "Gb" in name or "颗粒" in name:
                series[name][idx] = round(series[name][idx], 3)
            else:
                series[name][idx] = round(series[name][idx], 2)

    history = []
    for idx, d in enumerate(dates):
        row = {"date": d.strftime("%Y-%m-%d")}
        for name in all_specs:
            row[name] = series[name][idx]
        history.append(row)

    return {
        "title": "DRAM 现货价格走势",
        "subtitle": "颗粒级 + 模组级价格",
        "unit": "USD",
        "data_frequency": "日频 (工作日)",
        "time_range": f"2023-01-03 至 {END_DATE.strftime('%Y-%m-%d')}",
        "data_source": DATA_SOURCE_NOTE,
        "note": DAILY_DATA_NOTE,
        "specs_die": list(specs.keys()),
        "specs_module": list(module_specs.keys()),
        "specs": list(all_specs.keys()),
        "history": history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------------------------------------------
# DRAM Contract (Quarterly, 2021-Q1 to present)
# ------------------------------------------------------------------
def generate_dram_contract():
    """DRAM quarterly contract average prices."""
    now = datetime.now()
    quarters = generate_quarters(2021, 1, now.year, (now.month - 1) // 3 + 1)

    specs = {
        "DDR4 8GB PC": {"base": 25.0, "vol": 0.08},
        "DDR4 16GB PC": {"base": 48.0, "vol": 0.08},
        "DDR5 8GB PC": {"base": 32.0, "vol": 0.10},
        "DDR5 16GB PC": {"base": 62.0, "vol": 0.10},
        "DDR4 8GB×2 PC": {"base": 50.0, "vol": 0.08},
        "DDR5 8GB×2 PC": {"base": 64.0, "vol": 0.10},
        "DDR4 Server 16GB": {"base": 85.0, "vol": 0.06},
        "DDR5 Server 16GB": {"base": 125.0, "vol": 0.08},
    }

    random.seed(43)
    series = {}
    for name, cfg in specs.items():
        series[name] = random_walk(cfg["base"], len(quarters), 0.001, cfg["vol"])

    # Apply historical DRAM contract cycle (2021 peak -> 2022 decline -> 2023 crash -> 2024 recovery)
    for idx, q in enumerate(quarters):
        y, qnum = q["year"], q["quarter"]
        cycle = 1.0
        if y == 2021:
            cycle = 1.0 + 0.15 * ((qnum - 1) / 3)  # 1.0 -> 1.15 (peak)
        elif y == 2022:
            cycle = 1.15 - 0.30 * ((qnum - 1) / 3)  # 1.15 -> 0.85 (decline)
        elif y == 2023:
            cycle = 0.85 - 0.15 * ((qnum - 1) / 3)  # 0.85 -> 0.70 (crash bottom)
        elif y == 2024:
            cycle = 0.70 + 0.40 * ((qnum - 1) / 3)  # 0.70 -> 1.10 (recovery)
        elif y == 2025:
            cycle = 1.10 + 0.10 * ((qnum - 1) / 3)  # 1.10 -> 1.20 (continued uptrend)
        else:
            cycle = 1.20 + 0.05 * ((qnum - 1) / 3)

        for name in specs:
            base = specs[name]["base"]
            deviation = series[name][idx] / base - 1.0
            series[name][idx] = base * (1.0 + deviation * 0.5 + (cycle - 1.0) * 0.5)
            series[name][idx] = round(series[name][idx], 2)

    history = []
    for idx, q in enumerate(quarters):
        row = {
            "quarter": q["label"],
            "year": q["year"],
            "quarter_num": q["quarter"]
        }
        for name in specs:
            row[name] = series[name][idx]
        history.append(row)

    return {
        "title": "DRAM 合约平均价格",
        "subtitle": "季度合约均价 (PC + Server)",
        "unit": "USD",
        "data_frequency": "季度",
        "time_range": f"2021-Q1 至 {quarters[-1]['label']}",
        "data_source": DATA_SOURCE_NOTE,
        "note": QUARTERLY_DATA_NOTE,
        "specs_pc": ["DDR4 8GB PC", "DDR4 16GB PC", "DDR5 8GB PC", "DDR5 16GB PC", "DDR4 8GB×2 PC", "DDR5 8GB×2 PC"],
        "specs_server": ["DDR4 Server 16GB", "DDR5 Server 16GB"],
        "specs": list(specs.keys()),
        "history": history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------------------------------------------
# NAND Spot (Daily, 2023-01 to present)
# ------------------------------------------------------------------
def generate_nand_spot():
    """NAND daily spot prices (die + module)."""
    dates = generate_dates_daily(START_DATE, END_DATE)
    n = len(dates)

    # NAND颗粒 (Die) prices
    specs_die = {
        "128Gb TLC (16GB×8)": {"base": 3.80, "vol": 0.02, "drift": 0.0001},
        "256Gb TLC (32GB×8)": {"base": 6.50, "vol": 0.02, "drift": 0.0001},
        "512Gb TLC (64GB×8)": {"base": 12.00, "vol": 0.02, "drift": 0.0001},
        "1Tb TLC (128GB×8)": {"base": 22.00, "vol": 0.02, "drift": 0.0001},
    }

    # NAND模组 (eMMC / SSD) prices
    specs_module = {
        "32GB (4GB×8) eMMC": {"base": 4.50, "vol": 0.015, "drift": 0.0001},
        "64GB (8GB×8) eMMC": {"base": 7.00, "vol": 0.015, "drift": 0.0001},
        "128GB (16GB×8) eMMC": {"base": 11.50, "vol": 0.015, "drift": 0.0001},
        "256GB SSD": {"base": 24.00, "vol": 0.012, "drift": 0.0001},
        "512GB SSD": {"base": 42.00, "vol": 0.012, "drift": 0.0001},
        "1TB SSD": {"base": 72.00, "vol": 0.012, "drift": 0.0001},
    }

    all_specs = {**specs_die, **specs_module}

    random.seed(44)
    series = {}
    for name, cfg in all_specs.items():
        series[name] = random_walk(cfg["base"], n, cfg["drift"], cfg["vol"])

    # Apply NAND historical cycle (NAND was hit harder than DRAM in 2023)
    for idx, d in enumerate(dates):
        y, m = d.year, d.month
        cycle = 1.0
        if y == 2023 and m <= 6:
            cycle = 0.55 + 0.15 * ((m - 1) / 5)  # 0.55 -> 0.70
        elif y == 2023 and m <= 9:
            cycle = 0.70 + 0.10 * ((m - 7) / 2)  # 0.70 -> 0.80
        elif y == 2023:
            cycle = 0.80 + 0.15 * ((m - 10) / 2)  # 0.80 -> 0.95
        elif y == 2024 and m <= 6:
            cycle = 0.95 + 0.25 * ((m - 1) / 5)  # 0.95 -> 1.20
        elif y == 2024 and m <= 9:
            cycle = 1.20 + 0.05 * ((m - 7) / 2)  # 1.20 -> 1.25
        elif y == 2024:
            cycle = 1.25 - 0.05 * ((m - 10) / 2)  # 1.25 -> 1.22
        elif y == 2025:
            cycle = 1.22 + 0.08 * ((m - 1) / 11)  # gradual uptrend
        else:
            cycle = 1.30 + 0.03 * ((m - 1) / 11)

        for name in all_specs:
            base = all_specs[name]["base"]
            deviation = series[name][idx] / base - 1.0
            series[name][idx] = base * (1.0 + deviation * 0.6 + (cycle - 1.0) * 0.4)
            series[name][idx] *= (1 + random.gauss(0, 0.005))
            if "Gb" in name or "颗粒" in name:
                series[name][idx] = round(series[name][idx], 3)
            else:
                series[name][idx] = round(series[name][idx], 2)

    history = []
    for idx, d in enumerate(dates):
        row = {"date": d.strftime("%Y-%m-%d")}
        for name in all_specs:
            row[name] = series[name][idx]
        history.append(row)

    return {
        "title": "NAND Flash 现货价格走势",
        "subtitle": "颗粒级 + 模组级价格",
        "unit": "USD",
        "data_frequency": "日频 (工作日)",
        "time_range": f"2023-01-03 至 {END_DATE.strftime('%Y-%m-%d')}",
        "data_source": DATA_SOURCE_NOTE,
        "note": DAILY_DATA_NOTE,
        "specs_die": list(specs_die.keys()),
        "specs_module": list(specs_module.keys()),
        "specs": list(all_specs.keys()),
        "history": history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------------------------------------------
# NAND Contract (Quarterly, 2021-Q1 to present)
# ------------------------------------------------------------------
def generate_nand_contract():
    """NAND quarterly contract average prices."""
    now = datetime.now()
    quarters = generate_quarters(2021, 1, now.year, (now.month - 1) // 3 + 1)

    specs = {
        "32GB (4GB×8) eMMC": {"base": 5.50, "vol": 0.08},
        "64GB (8GB×8) eMMC": {"base": 8.50, "vol": 0.08},
        "128GB (16GB×8) eMMC": {"base": 14.00, "vol": 0.08},
        "256GB SSD": {"base": 26.00, "vol": 0.06},
        "512GB SSD": {"base": 45.00, "vol": 0.06},
        "1TB SSD": {"base": 78.00, "vol": 0.06},
    }

    random.seed(45)
    series = {}
    for name, cfg in specs.items():
        series[name] = random_walk(cfg["base"], len(quarters), 0.001, cfg["vol"])

    # NAND contract cycle (similar to spot but more smoothed)
    for idx, q in enumerate(quarters):
        y, qnum = q["year"], q["quarter"]
        cycle = 1.0
        if y == 2021:
            cycle = 1.0 + 0.10 * ((qnum - 1) / 3)
        elif y == 2022:
            cycle = 1.10 - 0.35 * ((qnum - 1) / 3)  # steeper decline
        elif y == 2023:
            cycle = 0.75 - 0.15 * ((qnum - 1) / 3)
        elif y == 2024:
            cycle = 0.60 + 0.45 * ((qnum - 1) / 3)  # strong recovery
        elif y == 2025:
            cycle = 1.05 + 0.10 * ((qnum - 1) / 3)
        else:
            cycle = 1.15 + 0.05 * ((qnum - 1) / 3)

        for name in specs:
            base = specs[name]["base"]
            deviation = series[name][idx] / base - 1.0
            series[name][idx] = base * (1.0 + deviation * 0.5 + (cycle - 1.0) * 0.5)
            series[name][idx] = round(series[name][idx], 2)

    history = []
    for idx, q in enumerate(quarters):
        row = {
            "quarter": q["label"],
            "year": q["year"],
            "quarter_num": q["quarter"]
        }
        for name in specs:
            row[name] = series[name][idx]
        history.append(row)

    return {
        "title": "NAND Flash 合约平均价格",
        "subtitle": "季度合约均价 (eMMC + SSD)",
        "unit": "USD",
        "data_frequency": "季度",
        "time_range": f"2021-Q1 至 {quarters[-1]['label']}",
        "data_source": DATA_SOURCE_NOTE,
        "note": QUARTERLY_DATA_NOTE,
        "specs_emmc": ["32GB (4GB×8) eMMC", "64GB (8GB×8) eMMC", "128GB (16GB×8) eMMC"],
        "specs_ssd": ["256GB SSD", "512GB SSD", "1TB SSD"],
        "specs": list(specs.keys()),
        "history": history,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------------------------------------------
# HBM Tracking (unchanged mostly, update dates)
# ------------------------------------------------------------------
def generate_hbm_tracking():
    return {
        "title": "HBM4 长协谈判时间线",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "events": [
            {"date": "2024-01-15", "event": "HBM4规格初步确认", "status": "completed", "detail": "JEDEC发布HBM4初步规格草案，带宽提升至2TB/s"},
            {"date": "2024-03-20", "event": "SK海力士开始样品验证", "status": "completed", "detail": "SK海力士向NVIDIA提交HBM4早期样品进行技术验证"},
            {"date": "2024-06-10", "event": "三星HBM4路线图公布", "status": "completed", "detail": "三星宣布2025年Q4量产HBM4，16层堆叠方案"},
            {"date": "2024-09-01", "event": "长协谈判启动", "status": "completed", "detail": "三大厂商与主要客户（NVIDIA、AMD、Google）开始2025-2027年长协谈判"},
            {"date": "2024-11-15", "event": "美光HBM4样品提交", "status": "completed", "detail": "美光向关键客户提交HBM4样品，12层方案"},
            {"date": "2025-01-15", "event": "Q1长协定稿预期", "status": "completed", "detail": "预计2025年Q1完成首批HBM4长协定价"},
            {"date": "2025-03-01", "event": "HBM4量产准备", "status": "in_progress", "detail": "预计2025年Q2开始小批量HBM4量产"},
            {"date": "2025-06-15", "event": "HBM4首批量产", "status": "upcoming", "detail": "SK海力士率先量产HBM4，12层堆叠16GB"},
            {"date": "2025-09-01", "event": "HBM4大规模出货", "status": "upcoming", "detail": "三星、美光跟进HBM4量产，供应量逐步爬坡"},
            {"date": "2026-01-01", "event": "HBM4长协全面执行", "status": "upcoming", "detail": "2026年长协全面落地，定价框架确定"}
        ]
    }

# ------------------------------------------------------------------
# Capacity Expansion (unchanged)
# ------------------------------------------------------------------
def generate_capacity_expansion():
    return {
        "title": "Memory Industry Capacity Expansion Plans",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "companies": [
            {
                "name": "SK Hynix",
                "ticker": "000660.KS",
                "plans": [
                    {"facility": "M15X (清州)", "type": "DRAM", "investment": "约5.3万亿韩元", "timeline": "2024-2026", "status": "建设中", "detail": "1a/1b nm DRAM产线，专注HBM和高性能DDR5"},
                    {"facility": "龙仁集群", "type": "DRAM/NAND", "investment": "约120万亿韩元", "timeline": "2027-2030", "status": "规划", "detail": "全球最大规模半导体集群，包含4座晶圆厂"},
                    {"facility": "大连NAND", "type": "NAND", "investment": "约3万亿韩元", "timeline": "2024-2025", "status": "扩产中", "detail": "收购Intel大连厂后扩产，增加96层/176层NAND产能"}
                ]
            },
            {
                "name": "Samsung Electronics",
                "ticker": "005930.KS",
                "plans": [
                    {"facility": "平泽P3", "type": "DRAM/NAND", "investment": "约30万亿韩元", "timeline": "2023-2025", "status": "运营中", "detail": "全球最大的半导体工厂，生产V9 NAND和1b nm DRAM"},
                    {"facility": "平泽P4", "type": "DRAM", "investment": "约25万亿韩元", "timeline": "2025-2027", "status": "建设中", "detail": "专注HBM3E和HBM4生产，1c nm DRAM产线"},
                    {"facility": "美国泰勒厂", "type": "Foundry/DRAM", "investment": "约170亿美元", "timeline": "2024-2026", "status": "建设中", "detail": "德州泰勒市新厂，响应美国CHIPS法案"}
                ]
            },
            {
                "name": "Micron Technology",
                "ticker": "MU",
                "plans": [
                    {"facility": "爱达荷州总部", "type": "DRAM", "investment": "约15亿美元", "timeline": "2024-2025", "status": "扩产中", "detail": "1β nm DRAM研发产线，HBM3E验证线"},
                    {"facility": "纽约州Clay厂", "type": "DRAM", "investment": "约100亿美元", "timeline": "2025-2028", "status": "建设中", "detail": "CHIPS法案支持，专注HBM和先进DRAM"},
                    {"facility": "日本广岛", "type": "DRAM/NAND", "investment": "约5000亿日元", "timeline": "2024-2026", "status": "扩产中", "detail": "1γ nm DRAM导入，与Tokyo Electron合作EUV"}
                ]
            }
        ]
    }

# ------------------------------------------------------------------
# Metadata
# ------------------------------------------------------------------
def generate_metadata():
    return {
        "dashboard_name": "存储行业可视化看板",
        "version": "1.1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "update_frequency": "每日2次（09:00, 21:00）",
        "data_sources": [
            "Yahoo Finance（股价）- 实时",
            "DRAMeXchange / TrendForce（存储价格）- 待接入",
            "公司财报（扩产计划）- 手动更新",
            "行业研报（深度报告）- ClawBot生成"
        ],
        "disclaimer": "本看板数据仅供参考，不构成投资建议。存储价格数据目前为模拟数据，待接入真实API。"
    }

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    os.makedirs("data", exist_ok=True)

    datasets = {
        "dram_spot": generate_dram_spot(),
        "dram_contract": generate_dram_contract(),
        "nand_spot": generate_nand_spot(),
        "nand_contract": generate_nand_contract(),
        "hbm_tracking": generate_hbm_tracking(),
        "capacity_expansion": generate_capacity_expansion(),
        "metadata": generate_metadata()
    }

    for key, data in datasets.items():
        filepath = f"data/{key}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Print size info
        size = os.path.getsize(filepath)
        n_records = len(data.get("history", []))
        print(f"Saved: {filepath} ({size:,} bytes, {n_records} records)")

    print(f"\nAll memory price data generated successfully.")
    print(f"Date range: 2023-01-03 to {END_DATE.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
