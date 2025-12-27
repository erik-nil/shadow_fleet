import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.utils import resample

# --- FILNAMN ---
SHADOW_FILE = "vessel_data/shadow_vessels.csv"  # Dina 600 bekräftade
UNKNOWN_FILE = "vessel_data/unknown_vessels.csv"  # Dina 8000 okända
OUTPUT_FILE = "suspect_vessels.csv"


def load_and_clean(filepath, label):
    """Laddar data och säkerställer rätt format på features."""
    df = pd.read_csv(filepath)

    # Beräkna ålder från byggår
    df["Built"] = pd.to_numeric(df["Built"], errors="coerce")
    df["Age"] = 2025 - df["Built"]

    # Konvertera numeriska värden
    df["GT"] = pd.to_numeric(df["GT"], errors="coerce")
    df["DWT"] = pd.to_numeric(df["DWT"], errors="coerce")

    # Sätt label
    df["is_shadow"] = label

    # Behåll endast relevanta kolumner för modellen + IMO för spårbarhet
    # TODO:Borde ta bort namn och IMO?
    cols_to_keep = ["IMO", "Name", "Type", "Flag", "Age", "GT", "DWT", "is_shadow"]
    return df[cols_to_keep]


def main():
    print("1. Laddar och förbereder datamängder...")
    shadow_df = load_and_clean(SHADOW_FILE, 1)
    unknown_df = load_and_clean(UNKNOWN_FILE, 0)

    # --- INGEN DOWNSAMPLING ---
    # Vi använder ALLA data för att få maximal information
    print(f"2. Slår ihop data: {len(shadow_df)} shadow + {len(unknown_df)} okända...")
    train_df = pd.concat([shadow_df, unknown_df])

    # --- DEFINIERA FEATURES ---
    features = ["Type", "Flag", "Age", "GT", "DWT"]
    X_train = train_df[features]
    y_train = train_df["is_shadow"]

    # --- BYGG PIPELINE ---
    # (Samma preprocessor som förut...)
    num_cols = ["Age", "GT", "DWT"]
    cat_cols = ["Type", "Flag"]

    num_transformer = SimpleImputer(strategy="median")
    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_cols),
            ("cat", cat_transformer, cat_cols),
        ]
    )

    # --- DEN VIKTIGA ÄNDRINGEN ---
    # class_weight='balanced' räknar automatiskt ut att shadow-fartyg är
    # mer sällsynta och gör dem viktigare för modellen.
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=12,
                    class_weight="balanced",  # <--- HÄR ÄR MAGIN
                    random_state=42,
                ),
            ),
        ]
    )

    print("3. Tränar modellen på hela datasetet...")
    model.fit(X_train, y_train)

    # --- PREDIKTION ---
    print("4. Analyserar...")
    X_unknown = unknown_df[features]
    probabilities = model.predict_proba(X_unknown)[:, 1]

    unknown_df["Shadow_Probability"] = probabilities

    # Filtrera på tröskelvärde
    threshold = 0.80
    priority_list = unknown_df[unknown_df["Shadow_Probability"] >= threshold]
    priority_list = priority_list.sort_values(by="Shadow_Probability", ascending=False)

    priority_list.to_csv(OUTPUT_FILE, index=False)

    print("-" * 40)
    print(
        f"KLART! {len(priority_list)} fartyg hittade med sannolikhet över {threshold*100}%."
    )


if __name__ == "__main__":
    main()
