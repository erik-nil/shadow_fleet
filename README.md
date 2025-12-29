# Shadow Fleet Intelligence Dashboard

## Overview
The **Shadow Fleet Intelligence Dashboard** is a data analytics tool designed to identify and visualize potential "shadow fleet" vessels. Ships often used to circumvent sanctions. 

The system uses a Random Forest Machine Learning model (`first_sort.py`) to assign a "Shadow Probability" score to vessels based on features such as **Age**, **Flag**, **Gross Tonnage (GT)**, and **Vessel Type**. The results are visualized in an interactive web dashboard built with **Plotly Dash**, this part was done with great help from an LLM (Gemini).

## Project Structure
```text
shadow_fleet/
├── app.py                      # Main dashboard application
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── vessels_with_score.csv      # Output data from the ML model (Input for App)
├── model/
│   └── first_sort.py           # ML script to train model and predict risk scores
├── scrapers/
│   ├── vesselfinder_scraper.py # Scrapes vessel technical data
│   ├── data_structurer.py      # Cleans and splits datasets
│   └── shadow_fleet_imo_names.csv #IMO numbers and names of shadow fleet vessels
└── vessel_data/
    ├── shadow_vessels.csv      # Training data (Known shadow vessels)
    └── unknown_vessels.csv     # Data to analyze (Unknown vessels)
```
## Data Sources

The project relies on two primary datasets collected on **2025-12-26**.

### 1. Known Shadow Fleet (`shadow_fleet_imo_names.csv`)
* **Source:** [War & Sanctions - Main Directorate of Intelligence (GUR)](https://war-sanctions.gur.gov.ua/en/transport/shadow-fleet)
* **Collection Method:** IMO numbers extracted manually by inspecting elements in Google Chrome.

### 2. General Vessel Population (`vessels.csv`)
* **Source:** [VesselFinder](https://www.vesselfinder.com)
* **Collection Method:** Scraped using the script `get_tankers.py`.
* **Filters Applied:**
    * **Vessel Type:** Tankers (Selected to ensure a manageable dataset size while focusing on the most relevant high-risk vessel category).

### 3. Processed Datasets
The general population (`vessels.csv`) was split into two separate datasets for analysis using `data_structurer.py`:

* **Confirmed Shadow Fleet (`shadow_vessels.csv`)**
    * **Description:** This dataset serves as the **ground truth** (positive labels) for the machine learning model. It contains vessels officially identified as participants in the shadow fleet.

* **Unknown Fleet (`unknown_vessels.csv`)**
    * **Description:** This dataset serves as the **candidate pool** (unlabeled/unknown data). The model analyzes these vessels to identify patterns and characteristics similar to the confirmed shadow fleet.

### Data Collection (Scrapers)

The project relies on data gathered from **VesselFinder**. The scraper uses **Selenium** with a connection to an existing Chrome instance to bypass bot detection.

#### Prerequisites: Chrome Debug Mode

The scraper requires Google Chrome to be running in **Remote Debugging Mode**.

1. Close all open Chrome windows.
2. Open a terminal/command prompt and run:

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp_chrome"

```

*(Adjust the path if Chrome is installed elsewhere on your system).*

A new Chrome window will open. Use this window for the scraping task.

#### Scraper: VesselFinder (Technical Data)

Collects mass data on vessels (Type, DWT, Built, Flag, etc.).

* **File:** `scrapers/vesselfinder_scraper.py`
* **Usage:**
1. In the debug Chrome window, navigate to `https://www.vesselfinder.com/vessels`.
2. Apply filters (e.g., Tankers).
3. Run the script:

python scrapers/vesselfinder_scraper.py




4. Input the **Start Page** and **End Page** when prompted.


* **Output:** A CSV file (`vesselfinder_tankers_full.csv`) containing raw vessel data.


## Dashboard Guide: How to Interpret the Data

The dashboard provides five key visualizations to analyze the fleet's risk profile. Here is how to read them:

### 1. Risk vs. Age (Scatter Plot)
* **What it shows:** Each dot represents a vessel.
    * **X-Axis:** Vessel Age (Older ships are further right).
    * **Y-Axis:** Gross Tonnage (Larger ships are higher up).
    * **Color:** Risk Score (🔴 Red = High Risk, 🟢 Green = Low Risk).
* **Insight:** Look for clusters of **red dots in the middle**. This indicates older, medium-sized tankers (often used for illicit ship-to-ship transfers) are being flagged as high risk.

### 2. Top 10 Flags (Bar Chart)
* **What it shows:** The most common flags of registration within your selected risk range.
* **Insight:** If you filter for "High Risk" (>0.8) and flags like **Panama** dominate this chart, it suggests these jurisdictions are heavily utilized by the shadow fleet.

### 3. Vessel Types (Pie Chart)
* **What it shows:** A breakdown of vessel categories (e.g., Oil Tankers, Chemical Tankers) in the current selection.
* **Insight:** Helps verify if the model is correctly targeting specific vessel classes known for sanctions evasion (e.g., Crude Oil Tankers).

### 4. Risk Score Distribution (Histogram)
* **What it shows:** How many vessels fall into each "risk bucket" (0% to 100%).
* **Insight:**
    * **Left-skewed (Green bars):** Most vessels are legitimate.
    * **Right-skewed (Red bars):** The model has identified a large number of high-risk targets.

### 5. Model Insights (Feature Importance)
* **Location:** Found in the "Model Insights" tab.
* **What it shows:** Which variables the AI considered most important when making decisions.
* **Insight:** **Flag** and **Age/Build year** have the longest bars, it confirms that the model is prioritizing the same indicators that human analysts use to identify shadow vessels.