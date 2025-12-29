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

## Data Sources

The project relies on two primary datasets collected on **2025-12-26**.

### 1. Known Shadow Fleet (`shadow_fleet.csv`)
* **Source:** [War & Sanctions - Main Directorate of Intelligence (GUR)](https://war-sanctions.gur.gov.ua/en/transport/shadow-fleet)
* **Collection Method:** Extracted manually by inspecting elements in Google Chrome.
* **Description:** This dataset serves as the **ground truth** (positive labels) for the machine learning model. It contains vessels officially identified as participants in the shadow fleet.

### 2. General Vessel Population (`vessels.csv`)
* **Source:** [VesselFinder](https://www.vesselfinder.com)
* **Collection Method:** Scraped using the script `get_tankers.py`.
* **Filters Applied:**
    * **Vessel Type:** Tankers (Selected to ensure a manageable dataset size while focusing on the most relevant high-risk vessel category).
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