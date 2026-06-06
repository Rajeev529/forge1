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

### 3. Generate the Audit Output
You can generate the SEO audit using any of the following three methods:

#### Method A: The Headless Runner (Fastest)
Use this for quick verification or grading. It processes the export and generates files in the `outputs/` folder.
```bash
python seo-command-center/run.py sample-export/
```

#### Method B: The Claude Code Plugin (Interactive)
If you are using Claude Code, you can run the audit directly as a skill:
```
/seo-audit sample-export/
```

#### Method C: Live Dashboard Mode (Visual)
To run the audit and immediately launch the interactive dashboard cockpit:
```bash
python seo-command-center/run_with_dashboard.py sample-export/
```
Then open your browser to: [http://localhost:7700](http://localhost:7700)

---

## 🛠 How it Works

### Deterministic Detection
The system follows a strict rulebook (`rulebook.md`) to identify issues. We use **plain Python** for counting, filtering, and detection to ensure 100% accuracy. LLMs are reserved only for high-value judgment tasks (e.g., rewriting titles or meta descriptions).

### Key Rules Implemented:
- **Titles**: Missing, Duplicate, Too Long (>60 chars), Too Short (<30 chars).
- **Meta Descriptions**: Missing, Duplicate, Too Long (>155 chars).
- **Headers**: Missing H1, Duplicate H1.
- **Technical**: Broken Links (4xx), Server Errors (5xx), Redirects (3xx), Redirect Chains.
- **Content**: Thin Content (<200 words), Orphan Pages, Non-indexable linked pages.
- **Performance**: Slow Pages (>1.0s response time).

## 📂 Project Structure
```
seo-command-center/
├── .claude-plugin/plugin.json   Plugin manifest
├── mcp/server.py                Local MCP server & Dashboard host (Port 7700)
├── seo/detector.py              Deterministic SEO detection engine
├── skills/seo-audit/SKILL.md    Plugin orchestrator
├── run.py                       Headless entry point
├── run_with_dashboard.py         Dashboard launch wrapper
├── populate_dashboard.py        Data synchronization script
└── outputs/                     Generated report.json and report.html
```

## 📋 Deliverables
All audits produce two primary artifacts in the `outputs/` directory:
- `report.json`: A machine-readable JSON file adhering to `report.schema.json`.
- `report.html`: A client-ready HTML report.
