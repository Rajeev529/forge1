
import sys
import os
import time
import importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))

print("Starting dashboard and populating with sample data...")

# Explicitly load the local server.py to avoid conflict with the 'mcp' SDK package
spec = importlib.util.spec_from_file_location("seo_server", os.path.join(ROOT, "mcp", "server.py"))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

# Start dashboard
server.start_dashboard()
print(f"[seo] dashboard live at http://localhost:{server.PORT}")

# Populate with sample data
try:
    print("Loading sample export...")
    server.seo_load("sample-export")

    print("Running detectors...")
    server.seo_detect()

    print("Generating report...")
    server.seo_report()

    print("Dashboard populated! You can now view it at http://localhost:7700")
except Exception as e:
    print(f"Error populating dashboard: {e}")
    import traceback
    traceback.print_exc()

# Keep the process alive so the daemon dashboard thread continues to run
print("Keeping server alive... Press Ctrl+C to stop.")
while True:
    time.sleep(60)
