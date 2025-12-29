# shadow_fleet

Shadow_fleet.csv data collected from https://war-sanctions.gur.gov.ua/en/transport/shadow-fleet at 2025-12-26 by inspecting in chrome window

Vessels.csv data scraped from vesselfinder.com at 2025-12-26. Vessel type was chosen as tanker to get a managable dataset.
The data vas scraped using get_tankers.py

# Shadow Fleet Intelligence Dashboard

## Overview
The **Shadow Fleet Intelligence Dashboard** is a data analytics tool designed to identify and visualize potential "shadow fleet" vessels—ships often used to circumvent sanctions. 

The system uses a Random Forest Machine Learning model (`first_sort.py`) to assign a "Shadow Probability" score to vessels based on features such as **Age**, **Flag**, **Gross Tonnage (GT)**, and **Vessel Type**. The results are visualized in an interactive web dashboard built with **Plotly Dash**.

## Project Structure

shadow_fleet/
├── app.py                      # Main dashboard application
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── vessels_with_score.csv      # Output data from the ML model (Input for App)
├── model/
│   └── first_sort.py           # ML script to train model and predict risk scores
└── vessel_data/
    ├── shadow_vessels.csv      # Training data (Known shadow vessels)
    └── unknown_vessels.csv     # Data to analyze (Unknown vessels)


