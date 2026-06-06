"""
Run with Dashboard Wrapper
A convenience script that launches the unified run.py in dashboard mode.
"""

import subprocess
import sys
import os

def main():
    # Determine the export directory
    export_dir = sys.argv[1] if len(sys.argv) > 1 else "sample-export"

    # Use absolute path to ensure consistency
    export_dir = os.path.abspath(export_dir)

    # Construct the command to run the unified entry point
    # We use sys.executable to ensure the same python environment is used
    cmd = [sys.executable, "seo-command-center/run.py", "--dashboard", export_dir]

    # If we are already inside seo-command-center, adjust the path
    if os.getcwd().endswith("seo-command-center"):
        cmd[1] = "run.py"

    print(f"Launching SEO Audit with Dashboard...")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error launching dashboard: {e}")

if __name__ == "__main__":
    main()
