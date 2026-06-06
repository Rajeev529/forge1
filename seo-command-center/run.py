"""
Run.py - Headless entry point for the SEO Command Center.
Orchestrates detection and reporting.
"""

import sys
import os
import time
from seo.detector import detect, load_rows, guess_site
from seo.report import generate_report

def main():
    # 1. Determine the export directory
    export_dir = sys.argv[1] if len(sys.argv) > 1 else "sample-export"
    export_dir = os.path.abspath(export_dir)

    print(f"Starting SEO Audit Process...")
    print(f"Target Export Directory: {export_dir}")

    try:
        # 2. Execute Detection Logic
        t0 = time.time()
        print("\nRunning deterministic detectors...")
        df = load_rows(export_dir)
        total_urls = len(df)
        site = guess_site(df)
        issues = detect(df)
        duration = round(time.time() - t0, 2)
        print(f"Detection complete. Found {len(issues)} issue types in {duration}s.")

        # 3. Generate Reports
        print("\nGenerating reports...")
        generate_report(
            issues=issues,
            site=site,
            urls_crawled=total_urls,
            duration=duration,
            output_dir="outputs"
        )

        print("\n" + "="*50)
        print("SEO Audit Complete!")
        print(f"Results are available in the 'outputs/' directory.")
        print("="*50)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
