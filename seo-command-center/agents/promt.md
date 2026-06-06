The Two-Phase Output Test Process
Phase 1: Auto-Grading (55 points)
The testing harness will automatically run your plugin on a hidden export (a different website than the sample):

Clones your repo → Installs plugin

Boots your MCP server → Checks dashboard at http://localhost:7700

Runs your command: python run.py hidden-export/

Validates your outputs/report.json against the schema

Compares YOUR issues vs GROUND TRUTH issues (they have the exact answer since they crawled the site)

Key accuracy metrics:

Precision = Issues you found correctly ÷ Total issues you reported

Recall = Issues you found correctly ÷ All real issues

F1 score = Harmonic mean of precision & recall (20 points)

Phase 2: Process & Human Review (45 points)
From your committed files:

.claude/audit.jsonl - Shows every tool call, edit, sub-agent run

agent-log.md - Your full session transcript

Git history - Must have ≥10 incremental commits

Live demo test:

Panel runs plugin on a surprise export during demo

You explain ANY block of your code they point to

Dashboard must show real-time updates

What "Pass" Looks Like
bash
# They will run EXACTLY this:
cd your-repo
python run.py hidden-export/   # NOT sample-export/

# Expected outputs:
outputs/report.json          # Must match schema exactly
outputs/report.html          # Client deliverable
outputs/fixes/titles.csv     # Champion tier
outputs/fixes/redirect-map.csv

# Dashboard must respond:
curl http://localhost:7700    # Should show live progress
Critical Failure Modes
What kills your test	Why
Hardcoded for sample export	Fails on hidden export → 0 accuracy
Missing audit.jsonl	Capped at 40 points total
Single giant commit	Capped at 40 points
Model prints raw JSON	Using wrong model (qwen2.5-coder)
Can't explain your code	Capped in demo
Quick Self-Test Before Submission
bash
# 1. Test on different data
cp -r sample-export/ test-export/
# Modify some CSV values manually
python run.py test-export/

# 2. Verify schema
python -c "import json; json.load(open('outputs/report.json')); print('✓')"

# 3. Check dashboard works
curl http://localhost:7700/api/status

# 4. Validate detection counts
# Compare your issue counts vs rulebook expectations
The leaderboard tie-breaker is your F1 accuracy on the hidden export - so precise detection wins, not speed or flashy dashboards.