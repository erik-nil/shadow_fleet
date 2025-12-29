import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

# --- 1. DATA PREP ---
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "vessels_with_score.csv")

try:
    df = pd.read_csv(csv_path)

    # Beräkna ålder
    if "Built" in df.columns:
        df["Age"] = 2025 - pd.to_numeric(df["Built"], errors="coerce").fillna(2025)

    # Fixa IMO
    df["IMO"] = (
        pd.to_numeric(df["IMO"], errors="coerce").fillna(0).astype(int).astype(str)
    )

    # Länk till MarineTraffic
    df["MT_Link"] = df["IMO"].apply(
        lambda x: f"[Link](https://www.marinetraffic.com/en/ais/details/ships/imo:{x})"
    )

    # Fixa Type
    if "Type" not in df.columns:
        df["Type"] = "Unknown"
    else:
        df["Type"] = df["Type"].fillna("Unknown")

except FileNotFoundError:
    print("WARNING: Data file not found. Using dummy data.")
    df = pd.DataFrame(
        {
            "IMO": ["0000000"],
            "Name": ["DUMMY"],
            "Type": ["Unknown"],
            "Shadow_Probability": [0.5],
            "Flag": ["Unknown"],
            "Age": [10],
            "GT": [10000],
            "MT_Link": ["#"],
        }
    )

# --- BERÄKNA GLOBALA GRAF-GRÄNSER (FÖR ATT LÅSA AXLARNA) ---
# Vi räknar ut max-värdena för HELA datasetet en gång, så vi kan låsa graferna till detta.
MAX_AGE = df["Age"].max() * 1.05 if "Age" in df.columns else 50
MAX_GT = df["GT"].max() * 1.05 if "GT" in df.columns else 100000

# Feature Importance Data
feature_data = pd.DataFrame(
    {
        "Variable": [
            "Age (Built)",
            "Flag",
            "Gross Tonnage (GT)",
            "Vessel Type",
            "DWT",
            "Length/Width",
        ],
        "Importance": [0.35, 0.30, 0.15, 0.10, 0.08, 0.02],
    }
)

# --- 2. LAYOUT ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container(
    [
        # --- HEADER & KONTROLLER (Fast del) ---
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.H2(
                                "Shadow Fleet Intelligence Dashboard",
                                className="text-center my-4",
                            ),  # Mer marginal (my-4)
                            width=12,
                        )
                    ]
                ),
                # KPI Kort (Mer luft med className="mb-4" och g-4 för gap mellan kolumner)
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [html.H6("Total Vessels"), html.H3(id="kpi-count")]
                                ),
                                color="primary",
                                inverse=True,
                                className="h-100 shadow-sm",
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [html.H6("Avg Age"), html.H3(id="kpi-age")]
                                ),
                                color="info",
                                inverse=True,
                                className="h-100 shadow-sm",
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [html.H6("Avg Risk Score"), html.H3(id="kpi-risk")]
                                ),
                                color="danger",
                                inverse=True,
                                className="h-100 shadow-sm",
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [html.H6("Dominant Flag"), html.H3(id="kpi-flag")]
                                ),
                                color="secondary",
                                inverse=True,
                                className="h-100 shadow-sm",
                            ),
                            width=3,
                        ),
                    ],
                    className="mb-4 g-3",
                ),  # g-3 ger utrymme MELLAN korten
                # Slider (Mer luft runt omkring)
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Risk Sensitivity Filter (0.00 - 1.00):",
                                    className="fw-bold mb-2",
                                ),
                                dcc.Slider(
                                    id="risk-slider",
                                    min=0,
                                    max=1,
                                    step=0.01,
                                    value=0.0,
                                    marks={
                                        0: "0%",
                                        0.5: "50%",
                                        0.8: "High Risk",
                                        1: "100%",
                                    },
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                            ],
                            width=12,
                        )
                    ],
                    className="mb-4 px-3",
                ),  # px-3 ger lite padding på sidorna
            ]
        ),
        # --- SCROLLABLE CONTENT ---
        html.Div(
            [
                dbc.Tabs(
                    [
                        # TAB 1: FLEET ANALYSIS
                        dbc.Tab(
                            label="Fleet Operations & Analysis",
                            children=[
                                html.Div(
                                    [  # Wrapper för padding inuti fliken
                                        # Rad 1: Scatter & Bar (Ökad höjd och marginaler)
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [  # Lägger grafer i kort för snyggare inramning
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="scatter-plot",
                                                                            style={
                                                                                "height": "45vh"
                                                                            },
                                                                        )  # Lite högre graf
                                                                    ]
                                                                )
                                                            ],
                                                            className="shadow-sm border-0",
                                                        )
                                                    ],
                                                    width=7,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="bar-chart",
                                                                            style={
                                                                                "height": "45vh"
                                                                            },
                                                                        )
                                                                    ]
                                                                )
                                                            ],
                                                            className="shadow-sm border-0",
                                                        )
                                                    ],
                                                    width=5,
                                                ),
                                            ],
                                            className="mb-4 g-4",
                                        ),  # Stort avstånd under och mellan
                                        # Rad 2: Pie & Histogram
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="type-pie-chart",
                                                                            style={
                                                                                "height": "40vh"
                                                                            },
                                                                        )
                                                                    ]
                                                                )
                                                            ],
                                                            className="shadow-sm border-0",
                                                        )
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="risk-histogram",
                                                                            style={
                                                                                "height": "40vh"
                                                                            },
                                                                        )
                                                                    ]
                                                                )
                                                            ],
                                                            className="shadow-sm border-0",
                                                        )
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-4 g-4",
                                        ),
                                        # Rad 3: Tabell
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    html.H4(
                                                                        "Detailed Vessel Database",
                                                                        className="m-0",
                                                                    )
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        dash_table.DataTable(
                                                                            id="vessel-table",
                                                                            columns=[
                                                                                {
                                                                                    "name": "IMO",
                                                                                    "id": "IMO",
                                                                                },
                                                                                {
                                                                                    "name": "Name",
                                                                                    "id": "Name",
                                                                                },
                                                                                {
                                                                                    "name": "Type",
                                                                                    "id": "Type",
                                                                                },
                                                                                {
                                                                                    "name": "Risk",
                                                                                    "id": "Shadow_Probability",
                                                                                    "type": "numeric",
                                                                                    "format": {
                                                                                        "specifier": ".3f"
                                                                                    },
                                                                                },
                                                                                {
                                                                                    "name": "Flag",
                                                                                    "id": "Flag",
                                                                                },
                                                                                {
                                                                                    "name": "Age",
                                                                                    "id": "Age",
                                                                                },
                                                                                {
                                                                                    "name": "GT",
                                                                                    "id": "GT",
                                                                                },
                                                                                {
                                                                                    "name": "Map",
                                                                                    "id": "MT_Link",
                                                                                    "presentation": "markdown",
                                                                                },
                                                                            ],
                                                                            data=[],
                                                                            page_action="native",
                                                                            page_current=0,
                                                                            page_size=15,
                                                                            sort_action="native",
                                                                            style_cell={
                                                                                "textAlign": "left",
                                                                                "padding": "12px",
                                                                                "fontSize": "13px",
                                                                            },  # Mer padding i cellerna
                                                                            style_header={
                                                                                "backgroundColor": "#f8f9fa",
                                                                                "fontWeight": "bold",
                                                                                "borderBottom": "2px solid #dee2e6",
                                                                            },
                                                                            style_data_conditional=[
                                                                                {
                                                                                    "if": {
                                                                                        "filter_query": "{Shadow_Probability} > 0.8"
                                                                                    },
                                                                                    "backgroundColor": "#fff3f3",
                                                                                    "color": "#d63031",
                                                                                }
                                                                            ],
                                                                        )
                                                                    ]
                                                                ),
                                                            ],
                                                            className="shadow-sm border-0",
                                                        )
                                                    ],
                                                    width=12,
                                                )
                                            ],
                                            className="mb-5",
                                        ),  # Extra marginal längst ner
                                    ],
                                    className="p-3",
                                )  # Padding runt hela flikens innehåll
                            ],
                        ),
                        # TAB 2: MODEL INSIGHTS
                        dbc.Tab(
                            label="Model Insights",
                            children=[
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardBody(
                                                                    [
                                                                        html.H4(
                                                                            "Feature Importance",
                                                                            className="mb-3",
                                                                        ),
                                                                        html.P(
                                                                            "These metrics correspond to the Random Forest model features used in 'first_sort.py'.",
                                                                            className="text-muted mb-4",
                                                                        ),
                                                                        dcc.Graph(
                                                                            id="feature-plot",
                                                                            figure=px.bar(
                                                                                feature_data.sort_values(
                                                                                    "Importance",
                                                                                    ascending=True,
                                                                                ),
                                                                                x="Importance",
                                                                                y="Variable",
                                                                                orientation="h",
                                                                                template="plotly_white",
                                                                                color="Importance",
                                                                                color_continuous_scale="Blues",
                                                                            ).update_layout(
                                                                                height=600
                                                                            ),
                                                                        ),
                                                                    ]
                                                                )
                                                            ],
                                                            className="shadow-sm border-0 mt-4",
                                                        )
                                                    ],
                                                    width=12,
                                                )
                                            ]
                                        )
                                    ],
                                    className="p-4",
                                )
                            ],
                        ),
                    ],
                    className="mt-3",
                )  # Marginal mellan tabs och innehåll
            ],
            style={"height": "100%", "overflowY": "auto"},
        ),
    ],
    fluid=True,
    style={
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "overflow": "hidden",
        "backgroundColor": "#f4f6f9",
    },  # Ljusgrå bakgrund för proffsigare look
)


# --- 3. CALLBACKS ---
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("type-pie-chart", "figure"),
        Output("risk-histogram", "figure"),
        Output("vessel-table", "data"),
        Output("kpi-count", "children"),
        Output("kpi-age", "children"),
        Output("kpi-risk", "children"),
        Output("kpi-flag", "children"),
    ],
    [Input("risk-slider", "value")],
)
def update_dashboard(min_risk):
    # Filtrera data
    filtered_df = df[df["Shadow_Probability"] >= min_risk].copy()
    filtered_df = filtered_df.sort_values(by="Shadow_Probability", ascending=False)

    # 1. Scatter Plot (LÅST AXEL)
    fig_scat = px.scatter(
        filtered_df,
        x="Age",
        y="GT",
        color="Shadow_Probability",
        size="GT",
        hover_data=["Name", "Flag", "Type"],
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 1],
        title="Risk vs Age (Fixed Axis)",
        template="plotly_white",
    )
    # Här låser vi axlarna till de globala maxvärdena vi räknade ut i början
    fig_scat.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(range=[0, MAX_AGE]),
        yaxis=dict(range=[0, MAX_GT]),
    )

    # 2. Bar Chart
    if len(filtered_df) > 0:
        flag_counts = filtered_df["Flag"].value_counts().nlargest(10).reset_index()
        flag_counts.columns = ["Flag", "Count"]
        fig_bar = px.bar(
            flag_counts,
            x="Flag",
            y="Count",
            title="Top 10 Flags",
            template="plotly_white",
            color="Count",
            color_continuous_scale="Blues",
        )
    else:
        fig_bar = px.bar(title="No Data")
    fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    # 3. Pie Chart
    if len(filtered_df) > 0:
        type_counts = filtered_df["Type"].value_counts()
        if len(type_counts) > 7:
            main_types = type_counts.nlargest(7).index
            filtered_df["Type_Clean"] = filtered_df["Type"].apply(
                lambda x: x if x in main_types else "Other"
            )
        else:
            filtered_df["Type_Clean"] = filtered_df["Type"]
        fig_pie = px.pie(
            filtered_df,
            names="Type_Clean",
            title="Vessel Types",
            hole=0.5,
            template="plotly_white",
        )
    else:
        fig_pie = px.pie(title="No Data")
    fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    # 4. Histogram (LÅST X-AXEL)
    fig_hist = px.histogram(
        filtered_df,
        x="Shadow_Probability",
        nbins=20,
        title="Risk Score Distribution",
        labels={"Shadow_Probability": "Risk Score"},
        template="plotly_white",
        color_discrete_sequence=["#e74c3c"],
    )
    # Låser X-axeln till 0-1 så man ser var i skalan urvalet befinner sig
    fig_hist.update_layout(
        margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(range=[0, 1]), bargap=0.1
    )

    # KPI Calculation
    count = len(filtered_df)
    avg_age = f"{filtered_df['Age'].mean():.1f} yrs" if count > 0 else "-"
    avg_risk = f"{filtered_df['Shadow_Probability'].mean():.2f}" if count > 0 else "-"
    dom_flag = filtered_df["Flag"].mode()[0] if count > 0 else "-"

    return (
        fig_scat,
        fig_bar,
        fig_pie,
        fig_hist,
        filtered_df.to_dict("records"),
        f"{count}",
        avg_age,
        avg_risk,
        dom_flag,
    )


if __name__ == "__main__":
    app.run(debug=True)
