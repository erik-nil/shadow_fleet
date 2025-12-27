import pandas as pd

# Read both CSV files
vessels_df = pd.read_csv("vessels.csv")
tankers_df = pd.read_csv("vesselfinder_tankers_full.csv")

# Find rows in tankers that are not in vessels
# Merge and find rows that only exist in tankers_df
merged = tankers_df.merge(vessels_df, how="left", indicator=True)
new_rows = merged[merged["_merge"] == "left_only"].drop("_merge", axis=1)

# Append new rows to vessels.csv
if len(new_rows) > 0:
    vessels_df = pd.concat([vessels_df, new_rows], ignore_index=True)
    vessels_df.to_csv("vessels.csv", index=False)
    print(f"Added {len(new_rows)} new lines to vessels.csv")
else:
    print("No new lines to add")
