"""
Run with Dashboard - Integration of the audit pipeline and the live dashboard.
Allows the user to see the audit progress live at http://localhost:7700.
"""
import os
import sys
import time

# Add ROOT to path so we can import from seo and mcp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from mcp_local.server import start_dashboard, seo_load, seo_detect, seo_report, seo_export

def main():
    export_dir = "sample-export"
    if len(sys.argv) > 1:
        export_dir = sys.argv[1]

    export_dir = os.path.abspath(export_dir)

    print(f"Starting SEO Audit with Live Dashboard...")
    print(f"Target Export Directory: {export_dir}")
    print(f"Dashboard live at http://localhost:7700")

    # 1. Start the dashboard server in a background thread
    start_dashboard()

    try:
        # 2. Load the data
        print("\nLoading export data...")
        load_res = seo_load(export_dir)
        print(f"Loaded {load_res['urls']} URLs for site: {load_res['site']}")

        # 3. Run detection
        print("Running detectors (updates dashboard in real-time)...")
        detect_res = seo_detect()
        print(f"Detected {detect_res['detected']} issue types.")

        # 4. Generate reports
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

        # Keep the process alive so the server keeps running
        print("\nServer is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
