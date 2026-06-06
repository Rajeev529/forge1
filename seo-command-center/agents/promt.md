# report.py - Instructions Only (No Code)

## Purpose
create at location seo-command-center/agents/report.py 
`report.py` is responsible for presenting SEO audit findings in a readable and exportable format. It receives issue data from `detector.py` and generates console output, JSON reports, and CSV reports.

This module is strictly part of the reporting layer and must not perform any SEO analysis or issue detection.

---

# Responsibilities

## 1. Console Report Generation

Generate a structured SEO audit report and display it in the terminal.

### Requirements

* Display a report header.

* Display the report generation timestamp.

* Group issues by severity.

* Display severity groups in the following order:

  1. High
  2. Medium
  3. Low

* Within the same severity level, sort issue types alphabetically.

* For each issue display:

  * Severity
  * Issue type
  * Total count
  * Affected URLs

* Sort URLs alphabetically.

* Display a maximum of the first 10 URLs.

* If more than 10 URLs exist:

  * Show the first 10 URLs.
  * Display a summary line using the format:

    ```
    ... and X more
    ```

* Skip issues with a count of zero.

---

## 2. JSON Report Export

Generate a JSON report file containing all issue information.

### Default Output Path

```
outputs/seo_report.json
```

### Requirements

* Automatically create the `outputs/` directory if it does not exist.
* Save the report in a human-readable format.
* Include a report generation timestamp in ISO format.
* Include the total number of issues found.
* Include all issue details.

### Expected Structure

Top-level fields:

* generated_at
* total_issues_found
* issues

Issue fields:

* severity
* count
* affected_urls

---

## 3. CSV Report Export

Generate a CSV report file containing issue data.

### Default Output Path

```
outputs/seo_report.csv
```

### Requirements

* Automatically create the `outputs/` directory if it does not exist.
* Store one issue-URL relationship per row.
* If an issue affects multiple URLs, create multiple rows.
* The CSV file should be suitable for filtering and spreadsheet analysis.

### Required Columns

1. issue_type
2. severity
3. url

---

# Class Specification

## Class Name

```
SEOReport
```

---

## Constructor

### Input

An issues dictionary provided by `detector.py`.

### Responsibilities

* Accept the issues dictionary.
* Store it internally as instance data.
* Treat the input data as read-only.
* Do not modify the original dictionary.

---

# Required Methods

## print_console_report()

### Purpose

Display a formatted SEO audit report in the terminal.

### Output

Human-readable console report.

---

## save_json_report(output_path)

### Purpose

Save the report as a JSON file.

### Default Path

```
outputs/seo_report.json
```

### Output

JSON report file.

---

## save_csv_report(output_path)

### Purpose

Save the report as a CSV file.

### Default Path

```
outputs/seo_report.csv
```

### Output

CSV report file.

---

# Console Report Format

The report should follow this structure:

* Separator line
* Report title
* Timestamp
* Separator line
* Severity-grouped issues
* URL listings
* Final separator line

Each issue section should contain:

* Severity
* Issue type
* Count
* Affected URLs

---

# Sorting Rules

## Severity Order

Issues must be displayed in this exact order:

1. High
2. Medium
3. Low

---

## Issue Type Order

Within the same severity level:

* Sort alphabetically by issue type name.

---

## URL Order

For every issue:

* Sort URLs alphabetically before displaying them.

---

# File Handling Rules

## Directory Management

Before writing any report:

* Verify that the output directory exists.
* Create it if necessary.

---

## JSON Export Rules

* Include ISO-formatted timestamp.
* Include total issue count.
* Use readable formatting.
* Preserve issue metadata and affected URLs.

---

## CSV Export Rules

* One row per issue-URL pair.
* Flat tabular structure.
* Consistent column naming.
* Suitable for spreadsheet tools and data analysis.

---

# Restrictions

## Do Not Perform Detection

This module must not:

* Crawl websites.
* Analyze pages.
* Detect SEO issues.
* Evaluate SEO rules.
* Generate findings.

Those responsibilities belong exclusively to `detector.py`.

---

## Do Not Modify Input Data

The issues dictionary must be treated as read-only.

Do not:

* Mutate data.
* Remove entries.
* Reorder the original structure.
* Alter issue contents.

---

## Do Not Use AI or LLMs

This module must not:

* Call AI services.
* Generate summaries using LLMs.
* Depend on external reasoning systems.

It is purely a reporting component.

---

# Dependencies

The implementation should support:

* JSON serialization
* File system operations
* Timestamp generation
* CSV export functionality

CSV generation may use either:

* Pandas
* Python's built-in CSV utilities

---

# Architecture Role

SEO Audit Workflow:

```
Crawler
   ↓
Detector
   ↓
Reporter
```

### Responsibilities

Crawler:

* Collects pages and site data.

Detector:

* Identifies SEO issues.

Reporter:

* Formats and presents results.

---

# Execution Flow

```
SEOReport receives issues
        ↓
print_console_report()
        ↓
save_json_report()
        ↓
save_csv_report()
```

---

# Summary

`report.py` is a presentation and export layer.

Its only responsibilities are:

* Formatting issue data
* Displaying issue data
* Exporting issue data

It must never perform crawling, detection, validation, or SEO analysis.

The module should remain focused on transforming issue data into clear, organized, and reusable reports.
