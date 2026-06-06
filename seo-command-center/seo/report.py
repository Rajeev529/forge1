"""Report Generator - Outputs SEO audit results strictly according to report.schema.json"""

import json
import csv
import os
from typing import List, Dict, Any

def generate_report(issues: List[Dict], site: str, urls_crawled: int, duration: float, output_dir: str = "outputs"):
    """
    Generates a comprehensive report that adheres strictly to report.schema.json.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Calculate Summary
    by_severity = {"High": 0, "Medium": 0, "Low": 0}
    total_urls_affected = set()

    for issue in issues:
        by_severity[issue["severity"]] += issue["count"]
        total_urls_affected.update(issue["affected_urls"])

    # 2. Construct JSON object according to report.schema.json
    report_data = {
        "site": site,
        "urls_crawled": urls_crawled,
        "summary": {
            "total_issues": len(issues),
            "by_severity": by_severity
        },
        "issues": issues,
        "fixes": {
            "titles": [], # Placeholder: populated by Fixer agent in later sprints
            "redirect_map": []
        },
        "recommendations": [], # Placeholder
        "run_meta": {
            "model": "deterministic",
            "model_calls": 0,
            "duration_sec": duration
        }
    }

    # Write JSON
    json_path = os.path.join(output_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # 3. Generate Basic report.html
    html_path = os.path.join(output_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <head><title>SEO Audit Report - {site}</title></head>
        <body>
            <h1>SEO Audit Report: {site}</h1>
            <p>URLs Crawled: {urls_crawled}</p>
            <p>Duration: {duration}s</p>
            <h2>Summary</h2>
            <ul>
                <li>High: {by_severity['High']}</li>
                <li>Medium: {by_severity['Medium']}</li>
                <li>Low: {by_severity['Low']}</li>
            </ul>
            <h2>Issues Found</h2>
            <table border="1">
                <tr><th>Issue</th><th>Severity</th><th>Count</th></tr>
                {''.join(f"<tr><td>{i['type']}</td><td>{i['severity']}</td><td>{i['count']}</td></tr>" for i in issues)}
            </table>
        </body>
        </html>
        """)

    # 4. Create Fixes directory (Required for Champion Tier / Criteria)
    fixes_dir = os.path.join(output_dir, "fixes")
    if not os.path.exists(fixes_dir):
        os.makedirs(fixes_dir)

    # Placeholders for Champion Tier
    for fix_file in ["titles.csv", "redirect-map.csv"]:
        with open(os.path.join(fixes_dir, fix_file), "w", encoding="utf-8") as f:
            f.write("URL,NewValue\n") # Basic header

    # 5. Console Output (Keep the nice visual summary)
    print("\n" + "="*50)
    print(" SEO AUDIT SUMMARY ".center(50, "="))
    print("="*50)
    for issue in issues:
        print(f"[{issue['severity']:<6}] {issue['type']:<25} | Count: {issue['count']}")
    print("-" * 50)
    print(f"Site: {site}")
    print(f"URLs Crawled: {urls_crawled}")
    print(f"Total Issue Types: {len(issues)}")
    print(f"Unique URLs Affected: {len(total_urls_affected)}")
    print(f"Breakdown: High({by_severity['High']}), Medium({by_severity['Medium']}), Low({by_severity['Low']})")
    print("="*50 + "\n")

    # 6. CSV Detailed Reports
    csv_dir = os.path.join(output_dir, "report_csvs")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    for issue in issues:
        csv_filename = f"{issue['type']}.csv"
        csv_path = os.path.join(csv_dir, csv_filename)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["URL"])
            for url in issue["affected_urls"]:
                writer.writerow([url])

    print(f"Reports written to: {output_dir}")
