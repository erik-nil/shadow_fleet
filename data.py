import pandas as pd
from sklearn.model_selection import train_test_split

# Create DataFrame and set IMO as the index
shadow_fleet_df = pd.read_csv("shadow_fleet.csv")
shadow_fleet_df.set_index("IMO", inplace=True)


all_fleet_df = pd.read_csv("vessels.csv")
all_fleet_df.set_index("IMO", inplace=True)
all_fleet_df.drop("Name", axis=1, inplace=True)

all_fleet_df["Shadow Fleet"] = all_fleet_df.index.isin(
    shadow_fleet_df.index.astype(int)
)

all_fleet_df_DATA = all_fleet_df.drop("Shadow Fleet", axis=1)
all_fleet_df_TARGET = all_fleet_df["Shadow Fleet"]

train_DATA, test_DATA, train_TARGET, test_TARGET = train_test_split(
    all_fleet_df_DATA, all_fleet_df_TARGET, test_size=0.2, random_state=42
)
