"""
Update daily report placeholder
This script is called by GitHub Actions or ClawBot to add/update reports.
ClawBot can push markdown reports to reports/ directory.
"""
import json
import os
from datetime import datetime

def generate_daily_report():
    """Generate daily report template"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = {
        "date": today,
        "title": f"存储行业日报 - {today}",
        "summary": "今日存储行业综述：",
        "market_assessment": "",
        "risk_alerts": [],
        "key_events": [],
        "price_analysis": "",
        "stock_analysis": "",
        "outlook": "",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save JSON version for dashboard
    os.makedirs("data", exist_ok=True)
    with open("data/latest_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Save markdown version for human editing
    os.makedirs("reports", exist_ok=True)
    md_path = f"reports/{today}.md"
    
    md_content = f"""# {report['title']}

> 更新时间: {report['last_updated']}
> 来源: ClawBot / 行业研报

## 市场综述

{report['summary']}

## 价格走势分析

（待ClawBot填写）

## 三大厂商动态

- **SK海力士**: 
- **三星电子**: 
- **美光科技**: 

## 今日交易评价

（待ClawBot填写）

## 风险提示

- 

## 明日展望

"""
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Update report index
    update_report_index()
    
    print(f"Generated report: {md_path}")
    return report

def update_report_index():
    """Update report index file"""
    reports = []
    if os.path.exists("reports"):
        for f in sorted(os.listdir("reports")):
            if f.endswith(".md"):
                date = f.replace(".md", "")
                reports.append({
                    "date": date,
                    "file": f"reports/{f}",
                    "title": f"存储行业日报 - {date}"
                })
    
    # Keep last 30 reports
    reports = reports[-30:]
    
    with open("data/reports_index.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reports": reports[::-1]  # Latest first
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Updated report index: {len(reports)} reports")

def main():
    report = generate_daily_report()
    print(f"Daily report template ready for ClawBot")

if __name__ == "__main__":
    main()
