"""SEO Detection Engine - Deterministic rules from internal_all.csv"""

import pandas as pd
from collections import defaultdict
import os

def detect(export_dir: str) -> list[dict]:
    """
    Analyzes the Screaming Frog internal_all.csv and detects 17 SEO issues.
    Returns a list of issue dicts: {type, severity, affected_urls, count, explanation}.
    """
    csv_path = os.path.join(export_dir, "internal_all.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find internal_all.csv in {export_dir}")

    # Load data using pandas as requested in prompt.md
    df = pd.read_csv(csv_path)

    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Helpers for safe conversion
    def get_int(col, default=0):
        return pd.to_numeric(df[col], errors='coerce').fillna(default).astype(int)

    def get_float(col, default=0.0):
        return pd.to_numeric(df[col], errors='coerce').fillna(default).astype(float)

    def get_str(col):
        return df[col].fillna("").astype(str).str.strip()

    # --- Pre-filters ---
    # 1. Only process rows where 'Content Type' contains "text/html"
    html_mask = get_str("Content Type").str.contains("text/html", case=False, na=False)
    df_html = df[html_mask].copy()

    # 2. Indexable 200 pages (used for titles, meta, H1, orphan, thin content)
    # Definition: Indexability == "Indexable" AND Status Code == 200
    idx_mask = (
        (get_str("Indexability") == "Indexable") &
        (get_int("Status Code") == 200)
    )
    # We apply this mask to the HTML subset
    df_idx200 = df_html[idx_mask].copy()

    issues = []

    def add_issue(type_name, severity, urls, explanation):
        # All URL lists must be sorted alphabetically per requirements
        sorted_urls = sorted(list(set(urls)))
        if sorted_urls:
            issues.append({
                "type": type_name,
                "severity": severity,
                "affected_urls": sorted_urls,
                "count": len(sorted_urls),
                "explanation": explanation
            })

    # --- 1. missing_title ---
    # Rule: Title 1 empty, indexable 200 page
    missing_title_urls = df_idx200[get_str("Title 1") == ""]["Address"].tolist()
    add_issue("missing_title", "High", missing_title_urls, "Indexable 200 pages with missing title tags.")

    # --- 2. duplicate_title ---
    # Rule: same Title 1 on 2+ indexable URLs
    # Filter out empty titles first to avoid counting them as duplicates
    title_series = get_str("Title 1")
    valid_titles_mask = (title_series != "") & idx_mask & html_mask

    title_counts = title_series[valid_titles_mask].value_counts()
    dup_title_vals = title_counts[title_counts > 1].index
    dup_title_urls = df[valid_titles_mask & (title_series.isin(dup_title_vals))]["Address"].tolist()
    add_issue("duplicate_title", "High", dup_title_urls, "Multiple indexable pages sharing the same title.")

    # --- 3. title_too_long ---
    # Rule: Title 1 Pixel Width > 561 OR Title 1 Length > 60
    title_long_mask = (get_float("Title 1 Pixel Width") > 561) | (get_int("Title 1 Length") > 60)
    # Apply to indexable pages
    title_long_urls = df_idx200[title_long_mask]["Address"].tolist()
    add_issue("title_too_long", "Medium", title_long_urls, "Titles that exceed recommended length or pixel width.")

    # --- 4. title_too_short ---
    # Rule: Title 1 Length < 30 (and not empty)
    title_short_mask = (get_int("Title 1 Length") < 30) & (get_str("Title 1") != "")
    title_short_urls = df_idx200[title_short_mask]["Address"].tolist()
    add_issue("title_too_short", "Low", title_short_urls, "Titles that are too short to be effective.")

    # --- 5. missing_meta_description ---
    # Rule: Meta Description 1 empty, indexable 200 page
    missing_meta_urls = df_idx200[get_str("Meta Description 1") == ""]["Address"].tolist()
    add_issue("missing_meta_description", "Medium", missing_meta_urls, "Indexable 200 pages with missing meta descriptions.")

    # --- 6. duplicate_meta_description ---
    # Rule: same Meta Description 1 on 2+ indexable URLs
    meta_series = get_str("Meta Description 1")
    valid_meta_mask = (meta_series != "") & idx_mask & html_mask

    meta_counts = meta_series[valid_meta_mask].value_counts()
    dup_meta_vals = meta_counts[meta_counts > 1].index
    dup_meta_urls = df[valid_meta_mask & (meta_series.isin(dup_meta_vals))]["Address"].tolist()
    add_issue("duplicate_meta_description", "Medium", dup_meta_urls, "Multiple indexable pages sharing the same meta description.")

    # --- 7. meta_description_too_long ---
    # Rule: Meta Description 1 Length > 155
    meta_long_mask = (get_int("Meta Description 1 Length") > 155)
    meta_long_urls = df_idx200[meta_long_mask]["Address"].tolist()
    add_issue("meta_description_too_long", "Low", meta_long_urls, "Meta descriptions that exceed 155 characters.")

    # --- 8. missing_h1 ---
    # Rule: H1-1 empty on a 200 page
    h1_missing_mask = (get_int("Status Code") == 200) & (html_mask) & (get_str("H1-1") == "")
    h1_missing_urls = df[h1_missing_mask]["Address"].tolist()
    add_issue("missing_h1", "Medium", h1_missing_urls, "Pages returning 200 OK but missing an H1 tag.")

    # --- 9. duplicate_h1 ---
    # Rule: same H1-1 on 2+ indexable URLs
    h1_series = get_str("H1-1")
    valid_h1_mask = (h1_series != "") & idx_mask & html_mask

    h1_counts = h1_series[valid_h1_mask].value_counts()
    dup_h1_vals = h1_counts[h1_counts > 1].index
    dup_h1_urls = df[valid_h1_mask & (h1_series.isin(dup_h1_vals))]["Address"].tolist()
    add_issue("duplicate_h1", "Low", dup_h1_urls, "Multiple indexable pages sharing the same H1 heading.")

    # --- 10. broken_link ---
    # Rule: Status Code in 400-499
    broken_mask = (get_int("Status Code") >= 400) & (get_int("Status Code") <= 499)
    broken_urls = df[broken_mask]["Address"].tolist()
    add_issue("broken_link", "High", broken_urls, "URLs returning a client error (4xx).")

    # --- 11. server_error ---
    # Rule: Status Code in 500-599
    server_err_mask = (get_int("Status Code") >= 500) & (get_int("Status Code") <= 599)
    server_err_urls = df[server_err_mask]["Address"].tolist()
    add_issue("server_error", "High", server_err_urls, "URLs returning a server error (5xx).")

    # --- 12. redirect ---
    # Rule: Status Code in 300-399
    redirect_mask = (get_int("Status Code") >= 300) & (get_int("Status Code") <= 399)
    redirect_urls = df[redirect_mask]["Address"].tolist()
    add_issue("redirect", "Medium", redirect_urls, "URLs that redirect (3xx).")

    # --- 13. redirect_chain ---
    # Rule: redirect whose Redirect URL is itself a redirecting URL
    redirect_df = df[redirect_mask]
    redirect_map = dict(zip(redirect_df["Address"], redirect_df["Redirect URL"]))

    chain_urls = []
    for source, target in redirect_map.items():
        if pd.isna(target) or target == "":
            continue
        if target in redirect_map:
            chain_urls.append(source)

    add_issue("redirect_chain", "High", chain_urls, "Redirects that lead to another redirect (chain).")

    # --- 14. thin_content ---
    # Rule: Word Count < 200 on an indexable page
    # Indexable page = (Indexability == "Indexable" AND Status Code == 200)
    thin_mask = (get_int("Word Count") < 200) & idx_mask & html_mask
    thin_urls = df[thin_mask]["Address"].tolist()
    add_issue("thin_content", "Low", thin_urls, "Indexable pages with low word count (< 200).")

    # --- 15. orphan_page ---
    # Rule: Inlinks = 0 on an indexable 200 page
    orphan_mask = (get_int("Inlinks") == 0) & idx_mask & html_mask
    orphan_urls = df[orphan_mask]["Address"].tolist()
    add_issue("orphan_page", "Medium", orphan_urls, "Indexable 200 pages with zero internal in-links.")

    # --- 16. non_indexable_but_linked ---
    # Rule: Indexability = 'Non-Indexable' AND Inlinks > 0
    non_idx_linked_mask = (get_str("Indexability") == "Non-Indexable") & (get_int("Inlinks") > 0)
    non_idx_linked_urls = df[non_idx_linked_mask]["Address"].tolist()
    add_issue("non_indexable_but_linked", "Medium", non_idx_linked_urls, "Pages marked as Non-Indexable but still have internal links.")

    # --- 17. slow_page ---
    # Rule: Response Time > 1.0
    slow_mask = (get_float("Response Time") > 1.0)
    slow_urls = df[slow_mask]["Address"].tolist()
    add_issue("slow_page", "Low", slow_urls, "Pages with response time greater than 1 second.")

    return issues

def summarize(issues: list[dict]) -> dict:
    by_sev = defaultdict(int)
    for i in issues:
        by_sev[i["severity"]] += 1
    return {
        "total_issues": len(issues),
        "by_severity": {
            "High": by_sev["High"],
            "Medium": by_sev["Medium"],
            "Low": by_sev["Low"]
        }
    }

if __name__ == "__main__":
    import sys, json
    d = sys.argv[1] if len(sys.argv) > 1 else "../sample-export"
    try:
        iss = detect(d)
        print(f"Loaded data from {d}, detected {len(iss)} issue types.")
        print(json.dumps(summarize(iss), indent=2))
        for i in iss:
            print(f"  [{i['severity']:<6}] {i['type']:<24} x{i['count']}")
    except Exception as e:
        print(f"Error: {e}")
