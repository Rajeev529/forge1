"""SEO Detection Engine - Deterministic rules from internal_all.csv"""

import pandas as pd
from collections import defaultdict
import os
from urllib.parse import urlparse

def load_rows(export_dir: str) -> pd.DataFrame:
    """Loads internal_all.csv from the export directory."""
    csv_path = os.path.join(export_dir, "internal_all.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find internal_all.csv in {export_dir}")
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    return df

def guess_site(df: pd.DataFrame) -> str:
    """Infers site name from the first URL."""
    if df.empty or "Address" not in df.columns:
        return "Unknown Site"
    first_url = str(df["Address"].iloc[0])
    parsed = urlparse(first_url)
    return parsed.netloc if parsed.netloc else first_url

def detect(df: pd.DataFrame) -> list[dict]:
    """
    Analyzes the Screaming Frog data and detects 17 SEO issues.
    Returns a list of issues.
    """
    total_urls = len(df)

    # --- Helper Dataframes for performance and avoiding warnings ---


    # --- Helper Dataframes for performance and avoiding warnings ---
    # All checks use these masks based on the original df
    html_mask = df["Content Type"].fillna("").str.contains("text/html", case=False)
    idx_mask = (df["Indexability"].fillna("") == "Indexable") & (pd.to_numeric(df["Status Code"], errors='coerce') == 200)

    # subset for indexable html pages
    df_idx200 = df[html_mask & idx_mask].copy()

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

    # 1. missing_title
    missing_title_urls = df_idx200[df_idx200["Title 1"].fillna("") == ""]["Address"].tolist()
    add_issue("missing_title", "High", missing_title_urls, "Indexable pages that have no title tag.")

    # 2. duplicate_title
    title_series = df["Title 1"].fillna("").str.strip()
    valid_titles_mask = (title_series != "") & html_mask & idx_mask
    title_counts = title_series[valid_titles_mask].value_counts()
    dup_title_vals = title_counts[title_counts > 1].index
    dup_title_urls = df[valid_titles_mask & (title_series.isin(dup_title_vals))]["Address"].tolist()
    add_issue("duplicate_title", "High", dup_title_urls, "Two or more indexable pages sharing the exact same title tag.")

    # 3. title_too_long
    pixel_width = pd.to_numeric(df_idx200["Title 1 Pixel Width"], errors='coerce').fillna(0)
    length = pd.to_numeric(df_idx200["Title 1 Length"], errors='coerce').fillna(0).astype(int)
    title_long_mask = (pixel_width > 561) | (length > 60)
    add_issue("title_too_long", "Medium", df_idx200[title_long_mask]["Address"].tolist(), "Title exceeds 60 characters or 561 pixels width.")

    # 4. title_too_short
    length = pd.to_numeric(df_idx200["Title 1 Length"], errors='coerce').fillna(0).astype(int)
    title_short_mask = (length < 30) & (df_idx200["Title 1"].fillna("") != "")
    add_issue("title_too_short", "Low", df_idx200[title_short_mask]["Address"].tolist(), "Title is less than 30 characters.")

    # 5. missing_meta_description
    missing_meta_urls = df_idx200[df_idx200["Meta Description 1"].fillna("") == ""]["Address"].tolist()
    add_issue("missing_meta_description", "Medium", missing_meta_urls, "Indexable pages with no meta description tag.")

    # 6. duplicate_meta_description
    meta_series = df["Meta Description 1"].fillna("").str.strip()
    valid_meta_mask = (meta_series != "") & html_mask & idx_mask
    meta_counts = meta_series[valid_meta_mask].value_counts()
    dup_meta_vals = meta_counts[meta_counts > 1].index
    dup_meta_urls = df[valid_meta_mask & (meta_series.isin(dup_meta_vals))]["Address"].tolist()
    add_issue("duplicate_meta_description", "Medium", dup_meta_urls, "Multiple indexable pages sharing the same meta description.")

    # 7. meta_description_too_long
    meta_length = pd.to_numeric(df_idx200["Meta Description 1 Length"], errors='coerce').fillna(0).astype(int)
    meta_long_mask = (meta_length > 155)
    add_issue("meta_description_too_long", "Low", df_idx200[meta_long_mask]["Address"].tolist(), "Meta description exceeds 155 characters.")

    # 8. missing_h1
    # H1 check is on 200 pages (not necessarily indexable)
    h1_mask = (pd.to_numeric(df["Status Code"], errors='coerce') == 200) & html_mask & (df["H1-1"].fillna("") == "")
    add_issue("missing_h1", "Medium", df[h1_mask]["Address"].tolist(), "Pages returning 200 OK but missing H1 heading tag.")

    # 9. duplicate_h1
    h1_series = df["H1-1"].fillna("").str.strip()
    valid_h1_mask = (h1_series != "") & html_mask & idx_mask
    h1_counts = h1_series[valid_h1_mask].value_counts()
    dup_h1_vals = h1_counts[h1_counts > 1].index
    dup_h1_urls = df[valid_h1_mask & (h1_series.isin(dup_h1_vals))]["Address"].tolist()
    add_issue("duplicate_h1", "Low", dup_h1_urls, "Multiple indexable pages sharing the same H1 heading.")

    # 10. broken_link
    status = pd.to_numeric(df["Status Code"], errors='coerce')
    broken_mask = (status >= 400) & (status <= 499)
    add_issue("broken_link", "High", df[broken_mask]["Address"].tolist(), "URLs returning 4xx client errors.")

    # 11. server_error
    server_err_mask = (status >= 500) & (status <= 599)
    add_issue("server_error", "High", df[server_err_mask]["Address"].tolist(), "URLs returning 5xx server errors.")

    # 12. redirect
    redirect_mask = (status >= 300) & (status <= 399)
    add_issue("redirect", "Medium", df[redirect_mask]["Address"].tolist(), "URLs that redirect (3xx).")

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
    word_count = pd.to_numeric(df_idx200["Word Count"], errors='coerce').fillna(0).astype(int)
    thin_mask = (word_count < 200)
    add_issue("thin_content", "Low", df_idx200[thin_mask]["Address"].tolist(), "Indexable pages with Word Count less than 200.")

    # 15. orphan_page
    inlinks = pd.to_numeric(df_idx200["Inlinks"], errors='coerce').fillna(0).astype(int)
    orphan_mask = (inlinks == 0)
    add_issue("orphan_page", "Medium", df_idx200[orphan_mask]["Address"].tolist(), "Indexable 200 pages with zero internal in-links.")

    # 16. non_indexable_but_linked
    non_idx_linked_mask = (df["Indexability"].fillna("") == "Non-Indexable") & (pd.to_numeric(df["Inlinks"], errors='coerce').fillna(0) > 0)
    add_issue("non_indexable_but_linked", "Medium", df[non_idx_linked_mask]["Address"].tolist(), "Pages marked as Non-Indexable but still have internal links.")

    # 17. slow_page
    res_time = pd.to_numeric(df["Response Time"], errors='coerce').fillna(0.0)
    slow_mask = (res_time > 1.0)
    add_issue("slow_page", "Low", df[slow_mask]["Address"].tolist(), "Pages with Response Time greater than 1.0 second.")

    return issues

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
