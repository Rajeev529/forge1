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

    # 3. Console Output (Keep the nice visual summary)
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

    # 4. CSV Detailed Reports
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
