import pandas as pd

# Config
INPUT_CSV = 'data/web_inventory_in.csv'
OUTPUT_CSV = 'data/web_inventory_out.csv'
REMOVED_LOG = 'data/web_inventory_removed.csv'

import pandas as pd

# Step 1: Load CSV
df = pd.read_csv(INPUT_CSV, dtype=str)

# Step 2: Clean 'Content Type' column
# Clean up and extract base content type from column.
df['Content Type Base'] = df["Content Type"].fillna("").str.split(";").str[0].str.strip().str.lower()
# Viewable content types to reain.
VIEWABLE_TYPES = [
    'text/html',
    'text/plain',
    'text/xml',
    'text/event-stream',
    'video/mp4',
    'application/xml',
]
# Create a mask for rows that are *not* viewable (to be removed)
non_viewable_mask = ~df['Content Type Base'].isin(VIEWABLE_TYPES)
# Log what we're removing
assets_removed = df[non_viewable_mask].copy()
# Keep viewable types
df = df[~non_viewable_mask]

# Step 3: Handle redirected rows.
# Identify redirect rows (HTTP 3xx)
df['Status Code'] = pd.to_numeric(df['Status Code'], errors='coerce')
redirect_mask = df['Status Code'].between(300, 399, inclusive='both')
# Create a new column to indicate whether it was updated
df['Redirect Processed'] = False
# Replace URL Encoded Address with Redirect Url for redirects
df.loc[redirect_mask, 'URL Encoded Address'] = df.loc[redirect_mask, 'Redirect URL']
# Mark those rows as processed
df.loc[redirect_mask, 'Redirect Processed'] = True

# Step 4: Combine log from each of the processing steps
removed_log = pd.concat([assets_removed])
removed_log.to_csv(REMOVED_LOG, index=False)

# Step 5: Save cleaned data
df.to_csv(OUTPUT_CSV, index=False)

# Print messages.
print(f"Cleaned file saved to {OUTPUT_CSV}, keeping {len(df)} rows.")
print(f"Logged {len(removed_log)} removed rows to {REMOVED_LOG}")
