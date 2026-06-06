# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
The repository contains the **SEO Command Center**, a Claude Code plugin designed to ingest Screaming Frog SEO exports, audit them against a deterministic rulebook, and provide both a live dashboard and a client report.

## Key Components
- **Core Logic**: `seo-command-center/seo/detector.py` (implements the rules from `rulebook.md`).
- **Infrastructure**: `seo-command-center/mcp/server.py` (hosts the live dashboard at `localhost:7700` and provides MCP tools).
- **Plugin Orchestration**: `seo-command-center/skills/seo-audit/SKILL.md` and the `/seo-audit` command.
- **Workflow Agents**: `seo-command-center/agents/` (ingest, auditor, fixer, reporter).
- **Entry Point**: `seo-command-center/run.py` (headless runner for testing and grading).

## Common Commands
- **Run End-to-End (Headless)**: `python seo-command-center/run.py sample-export/`
- **Use Plugin in Claude Code**: `/seo-audit sample-export/`
- **Install Dependencies**: `pip install mcp`
- **Live Dashboard**: Start `python seo-command-center/mcp/server.py` and visit `http://localhost:7700`

## Architecture & Constraints
- **Deterministic Audit**: Use `seo-command-center/seo/detector.py` for all rule-based detection. Do not use LLMs for basic counting/filtering of crawl rows.
- **LLM Usage**: Reserved for high-value judgment tasks: rewriting titles/meta descriptions and choosing redirect targets.
- **Validation**: All outputs in `outputs/report.json` must strictly adhere to `report.schema.json`.
- **Pre-filtering**: Always filter for `text/html` and indexable pages before performing title/meta/H1 checks.

## Project Memory & Records
This project is part of a graded challenge. The following files must be maintained:
- `seo-command-center/CLAUDE.md`: Project-specific memory and instructions.
- `seo-command-center/PROMPTS.md`: Log of key prompts used during development.
- `seo-command-center/DECISIONS.md`: Log of architectural and logic decisions.
- `.claude/audit.jsonl`: Auto-generated log of tool calls.
- `agent-log.md`: Session transcript (export using `bash seo-command-center/scripts/export-transcript.sh`).

## Reference Documents
- `rulebook.md`: The deterministic SEO rules for detection.
- `seo-command-center/README.md`: Quickstart and project structure.
