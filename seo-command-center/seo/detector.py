"""SEO Detection Engine - Deterministic rules from internal_all.csv"""

import pandas as pd
from collections import defaultdict
import os

def detect(export_dir: str) -> tuple[list[dict], int, str]:
    """
    Analyzes the Screaming Frog internal_all.csv and detects 17 SEO issues.
    Returns a tuple: (list of issue dicts, total_urls_crawled, site_name)
    """
    csv_path = os.path.join(export_dir, "internal_all.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find internal_all.csv in {export_dir}")

    # Load data using pandas
    df = pd.read_csv(csv_path)

    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Site name is usually the domain of the first address
    site_name = "Unknown Site"
    if not df.empty and "Address" in df.columns:
        first_url = df["Address"].iloc[0]
        try:
            from urllib.parse import urlparse
            site_name = urlparse(first_url).netloc
        except:
            pass

    # Helpers for safe conversion
    def get_int(col, default=0):
        return pd.to_numeric(df[col], errors='coerce').fillna(default).astype(int)

    def get_float(col, default=0.0):
        return pd.to_numeric(df[col], errors='coerce').fillna(default).astype(float)

    def get_str(col):
        return df[col].fillna("").astype(str).str.strip()

    # --- Pre-filters ---
    html_mask = get_str("Content Type").str.contains("text/html", case=False, na=False)
    df_html = df[html_mask].copy()

    idx_mask = (
        (get_str("Indexability") == "Indexable") &
        (get_int("Status Code") == 200)
    )
    df_idx200 = df_html[idx_mask].copy()

    issues = []

    def add_issue(type_name, severity, urls, explanation):
        sorted_urls = sorted(list(set(urls)))
        if sorted_urls:
            issues.append({
                "type": type_name,
                "severity": severity,
                "affected_urls": sorted_urls,
                "count": len(sorted_urls),
                "explanation": explanation
            })

    # Refined explanations based on the Fix Guide (issues.md)

    # 1. missing_title
    missing_title_urls = df_idx200[get_str("Title 1") == ""]["Address"].tolist()
    add_issue("missing_title", "High", missing_title_urls, "Indexable pages that have no title tag.")

    # 2. duplicate_title
    title_series = get_str("Title 1")
    valid_titles_mask = (title_series != "") & idx_mask & html_mask
    title_counts = title_series[valid_titles_mask].value_counts()
    dup_title_vals = title_counts[title_counts > 1].index
    dup_title_urls = df[valid_titles_mask & (title_series.isin(dup_title_vals))]["Address"].tolist()
    add_issue("duplicate_title", "High", dup_title_urls, "Two or more indexable pages sharing the exact same title tag.")

    # 3. title_too_long
    title_long_mask = (get_float("Title 1 Pixel Width") > 561) | (get_int("Title 1 Length") > 60)
    title_long_urls = df_idx200[title_long_mask]["Address"].tolist()
    add_issue("title_too_long", "Medium", title_long_urls, "Title exceeds 60 characters or 561 pixels width.")

    # 4. title_too_short
    title_short_mask = (get_int("Title 1 Length") < 30) & (get_str("Title 1") != "")
    title_short_urls = df_idx200[title_short_mask]["Address"].tolist()
    add_issue("title_too_short", "Low", title_short_urls, "Title is less than 30 characters.")

    # 5. missing_meta_description
    missing_meta_urls = df_idx200[get_str("Meta Description 1") == ""]["Address"].tolist()
    add_issue("missing_meta_description", "Medium", missing_meta_urls, "Indexable pages with no meta description tag.")

    # 6. duplicate_meta_description
    meta_series = get_str("Meta Description 1")
    valid_meta_mask = (meta_series != "") & idx_mask & html_mask
    meta_counts = meta_series[valid_meta_mask].value_counts()
    dup_meta_vals = meta_counts[meta_counts > 1].index
    dup_meta_urls = df[valid_meta_mask & (meta_series.isin(dup_meta_vals))]["Address"].tolist()
    add_issue("duplicate_meta_description", "Medium", dup_meta_urls, "Multiple indexable pages sharing the same meta description.")

    # 7. meta_description_too_long
    meta_long_mask = (get_int("Meta Description 1 Length") > 155)
    meta_long_urls = df_idx200[meta_long_mask]["Address"].tolist()
    add_issue("meta_description_too_long", "Low", meta_long_urls, "Meta description exceeds 155 characters.")

    # 8. missing_h1
    h1_missing_mask = (get_int("Status Code") == 200) & (html_mask) & (get_str("H1-1") == "")
    h1_missing_urls = df[h1_missing_mask]["Address"].tolist()
    add_issue("missing_h1", "Medium", h1_missing_urls, "Pages returning 200 OK but missing H1 heading tag.")

    # 9. duplicate_h1
    h1_series = get_str("H1-1")
    valid_h1_mask = (h1_series != "") & idx_mask & html_mask
    h1_counts = h1_series[valid_h1_mask].value_counts()
    dup_h1_vals = h1_counts[h1_counts > 1].index
    dup_h1_urls = df[valid_h1_mask & (h1_series.isin(dup_h1_vals))]["Address"].tolist()
    add_issue("duplicate_h1", "Low", dup_h1_urls, "Multiple indexable pages sharing the same H1 heading.")

    # 10. broken_link
    broken_mask = (get_int("Status Code") >= 400) & (get_int("Status Code") <= 499)
    broken_urls = df[broken_mask]["Address"].tolist()
    add_issue("broken_link", "High", broken_urls, "URLs returning 4xx client errors.")

    # 11. server_error
    server_err_mask = (get_int("Status Code") >= 500) & (get_int("Status Code") <= 599)
    server_err_urls = df[server_err_mask]["Address"].tolist()
    add_issue("server_error", "High", server_err_urls, "URLs returning 5xx server errors.")

    # 12. redirect
    redirect_mask = (get_int("Status Code") >= 300) & (get_int("Status Code") <= 399)
    redirect_urls = df[redirect_mask]["Address"].tolist()
    add_issue("redirect", "Medium", redirect_urls, "URLs that redirect (3xx).")

    # 13. redirect_chain
    redirect_df = df[redirect_mask]
    redirect_map = dict(zip(redirect_df["Address"], redirect_df["Redirect URL"]))
    chain_urls = []
    for source, target in redirect_map.items():
        if pd.isna(target) or target == "":
            continue
        if target in redirect_map:
            chain_urls.append(source)
    add_issue("redirect_chain", "High", chain_urls, "A redirect whose Redirect URL is itself a redirecting URL.")

    # 14. thin_content
    thin_mask = (get_int("Word Count") < 200) & idx_mask & html_mask
    thin_urls = df[thin_mask]["Address"].tolist()
    add_issue("thin_content", "Low", thin_urls, "Indexable pages with Word Count less than 200.")

    # 15. orphan_page
    orphan_mask = (get_int("Inlinks") == 0) & idx_mask & html_mask
    orphan_urls = df[orphan_mask]["Address"].tolist()
    add_issue("orphan_page", "Medium", orphan_urls, "Indexable 200 pages with zero internal in-links.")

    # 16. non_indexable_but_linked
    non_idx_linked_mask = (get_str("Indexability") == "Non-Indexable") & (get_int("Inlinks") > 0)
    non_idx_linked_urls = df[non_idx_linked_mask]["Address"].tolist()
    add_issue("non_indexable_but_linked", "Medium", non_idx_linked_urls, "Pages marked as Non-Indexable but still have internal links.")

    # 17. slow_page
    slow_mask = (get_float("Response Time") > 1.0)
    slow_urls = df[slow_mask]["Address"].tolist()
    add_issue("slow_page", "Low", slow_urls, "Pages with Response Time greater than 1.0 second.")

    return issues, len(df), site_name

def summarize(issues: list[dict]) -> dict:
    by_sev = defaultdict(int)
    for i in issues:
        by_sev[i["severity"]] += i["count"]
    return {
        "total_issues": len(issues),
        "by_severity": {
            "High": by_sev["High"],
            "Medium": by_sev["Medium"],
            "Low": by_sev["Low"]
        }
    }
