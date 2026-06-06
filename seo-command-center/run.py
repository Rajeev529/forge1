"""
Run.py - Unified entry point for the SEO Command Center.
Supports both headless execution (for grading/automation) and live dashboard mode.
"""

import sys
import os
import time

# Ensure the current directory is in the path for imports
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Base imports for headless mode
from seo.detector import detect, load_rows, guess_site
from seo.report import generate_report

def main():
    args = sys.argv[1:]

    # Check for dashboard flag
    dashboard_mode = False
    if "--dashboard" in args:
        dashboard_mode = True
        # Remove flag from args to leave only the directory path
        args = [arg for arg in args if arg != "--dashboard"]

    # Determine the export directory
    export_dir = args[0] if args else "sample-export"
    export_dir = os.path.abspath(export_dir)

    if dashboard_mode:
        # --- Dashboard Logic ---
        # Import inside the block to avoid dependency requirements for headless runs
        try:
            from mcp_local.server import start_dashboard, seo_load, seo_detect, seo_report, seo_export
        except ImportError as e:
            print(f"Error: Could not import mcp_local.server. Ensure dependencies are installed. {e}")
            sys.exit(1)

        print(f"Starting SEO Audit with Live Dashboard...")
        print(f"Target Export Directory: {export_dir}")
        print(f"Dashboard live at http://localhost:7700")

        start_dashboard()

        try:
            print("\nLoading export data...")
            load_res = seo_load(export_dir)
            print(f"Loaded {load_res['urls']} URLs for site: {load_res['site']}")

            print("Running detectors (updates dashboard in real-time)...")
            detect_res = seo_detect()
            print(f"Detected {detect_res['detected']} issue types.")

            print("Generating JSON report...")
            report_res = seo_report()
            print(f"Report saved to {report_res['path']}")

            print("Exporting HTML report...")
            export_res = seo_export()
            print(f"HTML report saved to {export_res['path']}")

            print("\n" + "="*50)
            print("Audit Complete!")
            print("You can view the live dashboard at http://localhost:7700")
            print("Or open the final HTML report: " + export_res['path'])
            print("="*50)

            print("\nServer is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # --- Headless Logic (Original / Grader Path) ---
        print(f"Starting SEO Audit Process (Headless)...")
        print(f"Target Export Directory: {export_dir}")

        try:
            t0 = time.time()
            print("\nRunning deterministic detectors...")
            df = load_rows(export_dir)
            total_urls = len(df)
            site = guess_site(df)
            issues = detect(df)
            duration = round(time.time() - t0, 2)
            print(f"Detection complete. Found {len(issues)} issue types in {duration}s.")

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
