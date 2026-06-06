# SEO Command Center — Forge Sprint 01

A Claude Code plugin designed to ingest Screaming Frog SEO exports, audit them against a deterministic rulebook, and provide both a live interactive dashboard and a client-ready report.

## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
The dashboard and MCP tools require the `mcp` library:
```bash
pip install mcp
```

---

## 🏃 How to Run the Project

Depending on your needs, you can run the audit in three different ways. All methods use the `sample-export/` directory as the default data source.

### Method A: Headless Runner (Fastest & Direct)
Use this for quick verification, grading, or when you only need the final files. It processes the export and generates all reports instantly.

**Command:**
```bash
python seo-command-center/run.py sample-export/
```

**Expected Output:**
- Console will print a detailed "SEO AUDIT SUMMARY" table showing:
  - Issue Type, Severity, and Count.
  - Total URLs crawled and total unique URLs affected.
- Process exits immediately after completion.

---

### Method B: Live Dashboard Mode (Visual & Interactive)
Use this to see the audit progress in real-time and explore issues through a web interface.

**Command:**
```bash
python seo-command-center/run_with_dashboard.py sample-export/
```

**Expected Output:**
- Console will notify you that the dashboard is live at `http://localhost:7700`.
- The script will stay running (until you press `Ctrl+C`).
- **Action:** Open your browser and visit [http://localhost:7700](http://localhost:7700) to see the live cockpit.

---

### Method C: Claude Code Plugin (AI Integrated)
If you are using Claude Code, you can run the audit directly as a skill.

**Command:**
```
/seo-audit sample-export/
```

---

## 📂 Expected Results & File Locations

After running any of the methods above, the system generates a comprehensive set of deliverables in the `seo-command-center/outputs/` directory:

### 1. Primary Reports
- `outputs/report.json`: The master machine-readable data file (adheres strictly to `report.schema.json`).
- `outputs/report.html`: A professional, client-ready visual report.

### 2. Detailed CSV Sheets (`outputs/report_csvs/`)
For every detected issue, a dedicated CSV is created containing the exact list of affected URLs.
- Examples: `broken_link.csv`, `duplicate_title.csv`, `slow_page.csv`, etc.

### 3. Fixes Directory (`outputs/fixes/`)
Contains implementation files for the suggested improvements:
- `titles.csv`: Proposed new title tags for affected pages.
- `redirect-map.csv`: Proposed mapping for redirect targets.

---

## 🛠 How it Works

### Deterministic Detection
The system follows a strict rulebook (`rulebook.md`) to identify issues. We use **plain Python (Pandas)** for counting, filtering, and detection to ensure 100% accuracy. LLMs are reserved only for high-value judgment tasks (e.g., rewriting titles or meta descriptions).

### Key Rules Implemented:
- **Titles**: Missing, Duplicate, Too Long (>60 chars), Too Short (<30 chars).
- **Meta Descriptions**: Missing, Duplicate, Too Long (>155 chars).
- **Headers**: Missing H1, Duplicate H1.
- **Technical**: Broken Links (4xx), Server Errors (5xx), Redirects (3xx), Redirect Chains.
- **Content**: Thin Content (<200 words), Orphan Pages, Non-indexable linked pages.
- **Performance**: Slow Pages (>1.0s response time).

## 🏗 Project Structure
```
seo-command-center/
├── .claude-plugin/plugin.json   Plugin manifest
├── mcp/server.py                Local MCP server & Dashboard host (Port 7700)
├── seo/detector.py              Deterministic SEO detection engine
├── skills/seo-audit/SKILL.md    Plugin orchestrator
├── run.py                       Headless entry point
├── run_with_dashboard.py         Dashboard launch wrapper
├── populate_dashboard.py        Data synchronization script
└── outputs/                     Generated reports and CSVs
```
