"""
Run.py - Headless entry point for the SEO Command Center.
Orchestrates detection and reporting.
"""

import sys
import os
from seo.detector import detect
from seo.report import generate_report

def main():
    # 1. Determine the export directory
    # Use first argument if provided, otherwise default to 'sample-export'
    export_dir = sys.argv[1] if len(sys.argv) > 1 else "sample-export"

    # Normalize path to avoid issues with relative paths
    export_dir = os.path.abspath(export_dir)

    print(f"🚀 Starting SEO Audit Process...")
    print(f"📁 Target Export Directory: {export_dir}")

    try:
        # 2. Execute Detection Logic (from seo/detector.py)
        print("\n🔍 Running deterministic detectors...")
        issues = detect(export_dir)
        print(f"✅ Detection complete. Found {len(issues)} issue types.")

        # 3. Generate Reports (from seo/report.py)
        print("\n📊 Generating reports...")
        # Default output folder is 'outputs' relative to current working directory
        generate_report(issues, output_dir="outputs")

        print("\n" + "="*50)
        print("🎉 SEO Audit Complete!")
        print(f"📂 Results are available in the 'outputs/' directory.")
        print("="*50)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure the export directory contains 'internal_all.csv'.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
