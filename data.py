import pandas as pd
from sklearn.model_selection import train_test_split

# Create DataFrame and set IMO as the index
shadow_fleet_df = pd.read_csv("shadow_fleet.csv")
shadow_fleet_df.set_index("IMO", inplace=True)

non_shadow_fleet_countries = pd.read_csv("non_shadow_fleet_countries.csv")

all_fleet_df = pd.read_csv("vessels.csv")
all_fleet_df.set_index("IMO", inplace=True)
all_fleet_df.drop("Name", axis=1, inplace=True)

all_fleet_df["Flag"] = all_fleet_df["Flag"].replace("-", pd.NA)

all_fleet_df["Shadow Fleet"] = pd.NA
all_fleet_df.loc[all_fleet_df.index.isin(shadow_fleet_df.index), 'Shadow Fleet'] = 1
all_fleet_df.loc[all_fleet_df['Shadow Fleet'].isna() & all_fleet_df['Flag'].isin(non_shadow_fleet_countries), 'Shadow Fleet'] = 0

pred_Data = all_fleet_df[all_fleet_df["Shadow Fleet"].isna()]
pred_Data.drop("Shadow Fleet", axis=1, inplace=True)

all_fleet_df["Shadow Fleet".isna()]
all_fleet_df = all_fleet_df[all_fleet_df["Shadow Fleet".notna()]]

# all_fleet_df_DATA = all_fleet_df.drop("Shadow Fleet", axis=1)
# all_fleet_df_TARGET = all_fleet_df["Shadow Fleet"]

# train_DATA, test_DATA, train_TARGET, test_TARGET = train_test_split(
#     all_fleet_df_DATA, all_fleet_df_TARGET, test_size=0.2, random_state=42
# )
