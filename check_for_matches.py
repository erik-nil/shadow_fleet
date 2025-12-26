import pandas as pd

# Load the CSV files
shadow_fleet_df = pd.read_csv("shadow_fleet_df.csv")
vesselfinder_tanker = pd.read_csv("vesselfinder_tankers_full.csv")

# Check if IMO numbers from shadow_fleet_df exist in vesselfinder_tanker
shadow_fleet_imo = set(shadow_fleet_df["IMO"].dropna())
vesselfinder_imo = set(vesselfinder_tanker["IMO"].dropna())

# Find matches and non-matches
matches = shadow_fleet_imo & vesselfinder_imo
non_matches = shadow_fleet_imo - vesselfinder_imo

print(f"\nTotal Shadow Fleet IMOs: {len(shadow_fleet_imo)}")
print(f"Total Vesselfinder IMOs: {len(vesselfinder_imo)}")
print(f"Matching IMO numbers: {len(matches)}")
print(f"Non-matching IMO numbers: {len(non_matches)}")

# Show matching vessels with details
if matches:
    matching_vessels = shadow_fleet_df[shadow_fleet_df["IMO"].isin(matches)].merge(
        vesselfinder_tanker[
            ["IMO", "Name", "Type", "Flag", "Built", "GT", "DWT", "Size"]
        ],
        on="IMO",
        how="inner",
        suffixes=("_shadow", "_vesselfinder"),
    )
    print(f"\n{matching_vessels}")
