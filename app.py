import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

# --- 1. DATA PREP ---


df = pd.read_csv("vessels_with_score.csv")  # Fyll i rätt filnamn

# Beräkna ålder
if "Built" in df.columns:
    df["Age"] = 2025 - pd.to_numeric(df["Built"], errors="coerce").fillna(2025)

# Fixa IMO för länk
df["IMO"] = pd.to_numeric(df["IMO"], errors="coerce").fillna(0).astype(int).astype(str)

# Skapa länk
df["MT_Link"] = df["IMO"].apply(
    lambda x: f"[Link](https://www.marinetraffic.com/en/ais/details/ships/imo:{x})"
)

# Säkerställ att Type finns (fyll med Unknown om den saknas)
if "Type" not in df.columns:
    df["Type"] = "Unknown"
else:
    df["Type"] = df["Type"].fillna("Unknown")

# --- DATA FÖR FEATURE IMPORTANCE (Platshållare - fyll i dina riktiga värden här) ---
# Hämta dessa från din Random Forest: print(model.feature_importances_)
feature_data = pd.DataFrame(
    {
        "Variable": [
            "Age",
            "Flag_Gabon",
            "Gross Tonnage",
            "Flag_Panama",
            "Manager_Location",
            "Type_Tanker",
        ],
        "Importance": [0.42, 0.28, 0.15, 0.08, 0.05, 0.02],
    }
)

# --- 2. LAYOUT ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    html.H2(
                        "Shadow Fleet Intelligence Dashboard",
                        className="text-center my-3",
                    ),
                    width=12,
                )
            ]
        ),
        # KPI Kort
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([html.H5("Vessels"), html.H3(id="kpi-count")]),
                        color="primary",
                        inverse=True,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([html.H5("Avg Age"), html.H3(id="kpi-age")]),
                        color="info",
                        inverse=True,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([html.H5("Risk Level"), html.H3(id="kpi-risk")]),
                        color="danger",
                        inverse=True,
                    ),
                    width=4,
                ),
            ],
            className="mb-4",
        ),
        # Slider (Nu högupplöst: steg på 0.01)
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label(
                            "Risk Sensitivity Filter (0.00 - 1.00):",
                            className="fw-bold",
                        ),
                        dcc.Slider(
                            id="risk-slider",
                            min=0,
                            max=1,
                            step=0.01,  # <--- HÖGUPPLÖST (1% steg)
                            value=0.0,
                            marks={0: "0%", 0.5: "50%", 0.8: "80%", 1: "100%"},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                    width=12,
                )
            ],
            className="mb-3",
        ),
        # --- FLIKAR FÖR ATT SKAPA UTRYMME ---
        dbc.Tabs(
            [
                # FLIK 1: Databas & Överblick
                dbc.Tab(
                    label="Fleet Operations & List",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="scatter-plot", style={"height": "40vh"}
                                        )
                                    ],
                                    width=8,
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="bar-chart", style={"height": "40vh"}
                                        )
                                    ],
                                    width=4,
                                ),
                            ],
                            className="mt-3 mb-3",
                        ),
                        # TABELLEN
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Vessel Database"),
                                        dash_table.DataTable(
                                            id="vessel-table",
                                            columns=[
                                                {"name": "IMO", "id": "IMO"},
                                                {"name": "Name", "id": "Name"},
                                                {
                                                    "name": "Type",
                                                    "id": "Type",
                                                },  # <--- NY KOLUMN
                                                {
                                                    "name": "Risk Score",
                                                    "id": "Shadow_Probability",
                                                    "type": "numeric",
                                                    "format": {"specifier": ".3f"},
                                                },  # 3 decimaler
                                                {"name": "Flag", "id": "Flag"},
                                                {"name": "Age", "id": "Age"},
                                                {
                                                    "name": "MarineTraffic",
                                                    "id": "MT_Link",
                                                    "presentation": "markdown",
                                                },
                                            ],
                                            data=[],
                                            # PAGINERING (Klicka dig vidare)
                                            page_action="native",
                                            page_current=0,
                                            page_size=15,  # 15 rader per sida
                                            sort_action="native",
                                            style_cell={
                                                "textAlign": "left",
                                                "padding": "8px",
                                            },
                                            style_header={
                                                "backgroundColor": "#f8f9fa",
                                                "fontWeight": "bold",
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {
                                                        "filter_query": "{Shadow_Probability} > 0.8"
                                                    },
                                                    "backgroundColor": "#ffe6e6",
                                                    "color": "black",
                                                }
                                            ],
                                        ),
                                    ],
                                    width=12,
                                )
                            ]
                        ),
                    ],
                ),
                # FLIK 2: Modellanalys (Feature Importance)
                dbc.Tab(
                    label="Model Insights (Feature Importance)",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4(
                                            "What drives the Risk Score?",
                                            className="mt-3",
                                        ),
                                        html.P(
                                            "This chart shows which variables the AI model considers most important when detecting shadow vessels."
                                        ),
                                        dcc.Graph(
                                            id="feature-plot",
                                            figure=px.bar(
                                                feature_data.sort_values(
                                                    "Importance", ascending=True
                                                ),
                                                x="Importance",
                                                y="Variable",
                                                orientation="h",
                                                title="Feature Importance (Random Forest)",
                                                template="plotly_white",
                                                color="Importance",
                                                color_continuous_scale="Blues",
                                            ).update_layout(height=500),
                                        ),
                                    ],
                                    width=12,
                                )  # Tar upp hela bredden
                            ]
                        )
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


# --- 3. CALLBACKS ---
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("vessel-table", "data"),
        Output("kpi-count", "children"),
        Output("kpi-age", "children"),
        Output("kpi-risk", "children"),
    ],
    [Input("risk-slider", "value")],
)
def update_all(min_risk):
    # Filtrera
    filtered_df = df[df["Shadow_Probability"] >= min_risk].copy()
    filtered_df = filtered_df.sort_values(by="Shadow_Probability", ascending=False)

    # Scatter
    fig_scat = px.scatter(
        filtered_df,
        x="Age",
        y="GT",
        color="Shadow_Probability",
        size="GT",
        hover_data=["Name", "Flag", "Type"],  # Type syns nu vid hover
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 1],
        title=f"Risk vs Age ({len(filtered_df)} vessels)",
        template="plotly_white",
    )
    fig_scat.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # Bar Chart (Flaggor)
    if len(filtered_df) > 0:
        flag_counts = filtered_df["Flag"].value_counts().nlargest(10).reset_index()
        flag_counts.columns = ["Flag", "Count"]
        fig_bar = px.bar(
            flag_counts, x="Flag", y="Count", title="Top Flags", template="plotly_white"
        )
    else:
        fig_bar = px.bar(title="No Data")
    fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # KPIer
    count = len(filtered_df)
    avg_age = f"{filtered_df['Age'].mean():.1f} yrs" if count > 0 else "-"
    avg_risk = f"{filtered_df['Shadow_Probability'].mean():.2f}" if count > 0 else "-"

    return (
        fig_scat,
        fig_bar,
        filtered_df.to_dict("records"),
        str(count),
        avg_age,
        avg_risk,
    )


if __name__ == "__main__":
    app.run(debug=True)
