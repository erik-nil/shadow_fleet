import pandas as pd
import numpy as np
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.utils import resample
import matplotlib.pyplot as plt
import seaborn as sns

# --- FILNAMN ---
SHADOW_FILE = (
    "vessel_data/shadow_vessels.csv"  # Bekräftade skuggfartyg / sakntionerade fartyg
)
UNKNOWN_FILE = "vessel_data/unknown_vessels.csv"  # ca 80000 okända tankerfartyg
OUTPUT_FILE = "vessels_with_score.csv"


def load_and_clean(filepath, label: int) -> pd.DataFrame:
    """Laddar data och säkerställer rätt format på features."""
    df = pd.read_csv(filepath)

    # Dela upp size
    df[["Length", "Width"]] = df["Size"].str.split("/", expand=True)
    df = df.drop("Size", axis=1)

    # Konvertera numeriska värden
    df["Built"] = pd.to_numeric(df["Built"], errors="coerce")
    df["GT"] = pd.to_numeric(df["GT"], errors="coerce")
    df["DWT"] = pd.to_numeric(df["DWT"], errors="coerce")
    df["Length"] = pd.to_numeric(df["Length"], errors="coerce")
    df["Width"] = pd.to_numeric(df["Width"], errors="coerce")

    # Slår ihop "-" och "Unknown"
    df["Flag"] = df["Flag"].replace("-", "Unknown")

    # Sätt label
    df["is_shadow"] = label

    return df

<<<<<<< HEAD

def exploratory_data_analysis(df: pd.DataFrame):
=======
def exploratory_data_analysis(df: pd.DataFrame) -> None:
>>>>>>> 86a03b4387e39941c202b86be8471f144e71dd6b
    """
    Utför enkel EDA på en DataFrame:
    - Visar grundläggande info
    - Summerar numeriska kolumner
    - Visar distributioner av kategoriska kolumner
    """
    # Grundläggande info
    print("INFO:")
    print(df.info())
    print("\nDESCRIBE:")
    print(df.describe())

    # Saknade värden
    print("\nMissing values per column:")
    print(df.isna().sum())

    # Kategoriska kolumner
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        print(f"\nValue counts for {col}:")
        print(df[col].value_counts(normalize=True))

    # Numeriska kolumner
    num_cols = df.select_dtypes(include="number").columns
    print("\nSummary statistics for numerical columns:")
    print(df[num_cols].describe())


def feature_selection(df: pd.DataFrame) -> None:

    ### Korrelation för numeriska cols
    num_cols = df.select_dtypes(include="number").columns.drop("is_shadow")
    corr_matrix = df[num_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")

    plt.show()  # VISAR PÅ LÅG KORRELATION FÖRUTOM MELLAN STORLEKSVARIABLERINA GT, DWT, LENGTH & WIDTH -> VI BESLUTAR ATT TA BORT WITDH OCH GT.


def feature_evaluation(df: pd.DataFrame, model: Pipeline) -> pd.DataFrame:

    ### Importance för olika variabler i modellen
    rf = model.named_steps["classifier"]
    feat_names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = rf.feature_importances_

    feat_imp_df = pd.DataFrame({"feature": feat_names, "importance": importances})

    feat_imp_df["feature"] = feat_imp_df["feature"].str.replace("cat__", "")
    feat_imp_df["feature"] = feat_imp_df["feature"].str.replace("num__", "")

    feat_imp_df["feature"] = feat_imp_df["feature"].str.split("_").str[0]

    feat_imp_df = feat_imp_df.groupby("feature")["importance"].sum().reset_index()
    feat_imp_df = feat_imp_df.sort_values(by="importance", ascending=False)

    return feat_imp_df


def model_building(train_df: pd.DataFrame, features: list[str]) -> Pipeline:
    X_train = train_df[features]
    y_train = train_df["is_shadow"]

    num_cols = X_train.select_dtypes(include="number").columns.tolist()
    cat_cols = X_train.select_dtypes(include="object").columns.tolist()

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

    rf_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=12,
                    class_weight="balanced", 
                    random_state=42,
                    oob_score=True,
                ),
            ),
        ]
    )

    rf_model.fit(X_train, y_train)

    return rf_model


def model_prediction(
    unknown_df: pd.DataFrame, features: list[str], model: Pipeline
) -> pd.DataFrame:
    X_unknown = unknown_df[features]
    unknown_df["Shadow_Probability"] = model.predict_proba(X_unknown)[:, 1]

    # Filtrera på tröskelvärde
    threshold = 0.0
    suspect_df = unknown_df[unknown_df["Shadow_Probability"] >= threshold]
    suspect_df = suspect_df.sort_values(by="Shadow_Probability", ascending=False)

    return suspect_df


def model_oob_evaluation(model: Pipeline) -> int:
    ### Beräknar OOB-score
    rf = model.named_steps["classifier"]
    oob_score = rf.oob_score_
    return oob_score

def model_sensitivity_evaluation(shadow_df: pd.DataFrame, model: Pipeline) -> int:

    ### Beräknar sensitivity för modellen
    X_shadow = model.named_steps["preprocessor"].transform(shadow_df[features])
    y_pred = model.named_steps["classifier"].predict(X_shadow)
    sensitivity = y_pred.mean()  # andelen korrekt klassade shadow-fartyg
    return sensitivity


if __name__ == "__main__":

    shadow_df = load_and_clean(SHADOW_FILE, 1)
    unknown_df = load_and_clean(UNKNOWN_FILE, 0)

    full_df = pd.concat([shadow_df, unknown_df])

    exploratory_data_analysis(full_df)

    feature_selection(full_df)

    features = ["Type", "Flag", "Built", "DWT", "Length"]
    model = model_building(full_df, features)

    suspect_df = model_prediction(unknown_df, features, model)

    feature_importance = feature_evaluation(full_df, model)

    oob_score = model_oob_evaluation(model)
    sensitivity = model_sensitivity_evaluation(shadow_df, model)

    metrics = {
        "sensitivity": sensitivity,
        "oob_score": oob_score,
    }
    with open("model_metrics.json", "w") as f:
        json.dump(metrics, f)
