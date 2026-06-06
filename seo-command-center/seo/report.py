"""Report Generator - Outputs SEO audit results to Console, JSON, and CSV"""

import json
import csv
import os
from typing import List, Dict

def generate_report(issues: List[Dict], output_dir: str = "outputs"):
    """
    Generates a comprehensive report from the detected issues.
    Saves results to:
    - outputs/report.json (Structured JSON)
    - outputs/report_csvs/ (One CSV per issue type)
    - Console (Summary)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Console Summary
    print("\n" + "="*50)
    print(" SEO AUDIT SUMMARY ".center(50, "="))
    print("="*50)

    total_urls_affected = set()
    by_severity = {"High": 0, "Medium": 0, "Low": 0}

    for issue in issues:
        by_severity[issue["severity"]] += issue["count"]
        total_urls_affected.update(issue["affected_urls"])
        print(f"[{issue['severity']:<6}] {issue['type']:<25} | Count: {issue['count']}")

    print("-" * 50)
    print(f"Total Issue Types Found: {len(issues)}")
    print(f"Unique URLs Affected:    {len(total_urls_affected)}")
    print(f"Total Issue Instances:   {sum(by_severity.values())}")
    print(f"Breakdown: High({by_severity['High']}), Medium({by_severity['Medium']}), Low({by_severity['Low']})")
    print("="*50 + "\n")

    # 2. JSON Report (Strict adherence to schema)
    # The schema usually expects an 'issues' list and a 'summary' object
    report_data = {
        "summary": {
            "total_issues": len(issues),
            "total_affected_urls": len(total_urls_affected),
            "severity_counts": by_severity
        },
        "issues": issues
    }

    json_path = os.path.join(output_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Successfully wrote JSON report to: {json_path}")

    # 3. CSV Detailed Reports (One per issue type for client clarity)
    csv_dir = os.path.join(output_dir, "report_csvs")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    for issue in issues:
        csv_filename = f"{issue['type']}.csv"
        csv_path = os.path.join(csv_dir, csv_filename)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["URL"]) # Header
            for url in issue["affected_urls"]:
                writer.writerow([url])

    print(f"Detailed CSVs written to: {csv_dir}")

if __name__ == "__main__":
    # Mock data for testing
    mock_issues = [
        {
            "type": "missing_title",
            "severity": "High",
            "affected_urls": ["http://example.com/1", "http://example.com/2"],
            "count": 2,
            "explanation": "Indexable 200 pages with missing title tags."
        },
        {
            "type": "slow_page",
            "severity": "Low",
            "affected_urls": ["http://example.com/slow"],
            "count": 1,
            "explanation": "Pages with response time greater than 1 second."
        }
    ]
    generate_report(mock_issues)
