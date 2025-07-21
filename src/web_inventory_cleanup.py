import json
import pandas as pd

# --- Config ---
INPUT_CSV = 'data/web_inventory_in.csv'
OUTPUT_CSV = 'data/web_inventory_out.csv'
REMOVED_LOG = 'data/web_inventory_removed.csv'
CLUSTER_JSON = 'data/cluster_definitions.json'
TAG_JSON = 'data/tag_definitions.json'

VIEWABLE_TYPES = {
    'text/html', 'text/plain', 'text/event-stream', 'video/mp4'
}
COMMON_ASSET_EXTENSIONS = (
    ".js", ".css", ".xml", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".ico", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".webmanifest"
)
NONSTATIC_COLUMNS = {"Keep?", "Response Time", "Response Header: Date", "Crawl Timestamp"}

# --- Load data ---
df = pd.read_csv(INPUT_CSV, dtype=str)
# --- Initial cleanup ---
df.fillna("", inplace=True)
# --- Clean derived columns ---
df["Status Code"] = pd.to_numeric(df["Status Code"], errors="coerce")
df["Crawl Depth"] = pd.to_numeric(df["Crawl Depth"], errors="coerce")
df["Content Type Base"] = (
    df.get("Content Type", "")
      .str.split(";").str[0]
      .str.strip().str.lower()
      .replace("", pd.NA)
)
df["First Path Segment"] = df["Path"].str.strip("/").str.split("/").str[0]

# --- Step 1: De-duplication ---
dedupe_cols = [c for c in df.columns if c not in NONSTATIC_COLUMNS]
dup_mask = df.duplicated(subset=dedupe_cols, keep="first")
deduped_rows = df[dup_mask].assign(Processed="General Duplicate")
df = df[~dup_mask]

# --- Step 2: Remove non-viewable ---
asset_mask = (
    (df["Content Type Base"].notna() & ~df["Content Type Base"].isin(VIEWABLE_TYPES)) |
    df["Path"].str.lower().str.endswith(COMMON_ASSET_EXTENSIONS)
)
assets_removed = df[asset_mask].assign(Processed="Asset")
df = df[~asset_mask]

# --- Step 3: Redirect handling ---
all_addresses = set(df["Address"])
redirect_mask = pd.Series(False, index=df.index)

# A. Redirect URL already in data
mask_a = df["Redirect URL"].ne("") & df["Redirect URL"].isin(all_addresses)
df.loc[mask_a, "Processed"] = "Destination Represented"
redirect_mask |= mask_a

# B. HTTP → HTTPS upgrade
is_http = df["Address"].str.startswith("http://")
https_version = df["Redirect URL"].str.replace("http://", "https://", n=1)
mask_b = (
    df["Status Code"].between(300, 399, inclusive="both") &
    is_http &
    https_version.isin(all_addresses) &
    (df["Redirect URL"] == https_version)
)
df.loc[mask_b, "Processed"] = "HTTP Upgrade"
redirect_mask |= mask_b

# C. HTTP → HTTPS duplicate check.
# Drop the http version if there is a matching https version.
http_to_https = df["Address"].str.replace("http://", "https://", n=1)
mask_c = (
    is_http &
    http_to_https.isin(all_addresses) &
    df["Redirect URL"].eq("") &
    ~df.index.isin(df[redirect_mask].index)
)
df.loc[mask_c, "Processed"] = "HTTP Duplicate"
redirect_mask |= mask_c

redirected_rows = df[redirect_mask]
df = df[~redirect_mask]

# --- Step 4: Clustering ---
with open(CLUSTER_JSON) as f:
    PATH_BASED_CLUSTERS = json.load(f)

def get_cluster(row):
    base = PATH_BASED_CLUSTERS.get(row["Reverse Domain"])
    if not base:
        return None
    return f"{base}/{row['First Path Segment']}" if row["First Path Segment"] else base

df["Clusters"] = df.apply(get_cluster, axis=1)

# --- Step 5: Tagging ---
# A. Group by status code.
def get_status_group(code):
    if pd.isna(code):
        return None
    code = int(code)
    if code == 200:
        return "Status: OK"
    elif 201 <= code <= 299:
        return "Status: Other Success"
    elif 300 <= code <= 399:
        return "Status: Unrepresented Redirect"
    elif code in (401, 403):
        return "Status: Access Denied"
    elif 400 <= code < 500:
        return "Status: Client Error"
    elif 500 <= code < 600:
        return "Status: Server Error"
    return None
df["Status Group"] = df["Status Code"].apply(get_status_group)

# B. Tagging based on patterns.
with open(TAG_JSON) as f:
    tag_rules = json.load(f)

extra_loop_tags = set(tag_rules.get("extra_loop", []))
domain_tag_map = {}

def tag_row_from_rules(row):
    tags = set()
    for substr, tag in tag_rules.get("address_contains", {}).items():
        if substr in row["Address"]:
            tags.add(tag)
    for substr, tag in tag_rules.get("reverse_domain_contains", {}).items():
        if substr in row["Reverse Domain"]:
            tags.add(tag)
    for substr, tag in tag_rules.get("title_contains", {}).items():
        if substr.lower() in row.get("Title 1", "").lower():
            tags.add(tag)
    for tag in tags & extra_loop_tags:
        domain = row["Reverse Domain"]
        if domain:
            domain_tag_map.setdefault(domain, set()).add(tag)
    return tags

df["Tags"] = df.apply(tag_row_from_rules, axis=1)

# Extra loop to tag based on shared reverse domain.
def group_reverse_domain(row):
    base_tags = row["Tags"] if isinstance(row["Tags"], set) else set()
    extra = domain_tag_map.get(row["Reverse Domain"], set())
    combined = base_tags | extra
    return ", ".join(sorted(tag for tag in combined if tag))

df["Tags"] = df.apply(group_reverse_domain, axis=1)


# --- Step 6: Save removed rows ---
removed_log = pd.concat([deduped_rows, assets_removed, redirected_rows])
removed_log.to_csv(REMOVED_LOG, index=False)

# --- Step 7: Final cleanup and save ---
df.drop(columns=["Content Type Base", "First Path Segment"], inplace=True)
df.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaned file saved to {OUTPUT_CSV}, keeping {len(df)} rows.")
print(f"Logged {len(removed_log)} removed rows to {REMOVED_LOG}")