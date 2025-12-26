import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# 1. Connect to existing Chrome session
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# 2. Load IMO list
input_df = pd.read_csv("shadow_fleet_df.csv")
imo_list = input_df["IMO"].tolist()

results_data = []


def scrape_particulars(input_imo):
    try:
        # Wait up to 10 seconds for the details to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "sFlagCur")))

        # Get Current Name for logging/ML
        ship_name = driver.find_element(By.ID, "sNameCur").text.strip()

        # 1. Flag & History
        current_flag = driver.find_element(By.ID, "sFlagCur").text.strip()
        history_element = driver.find_element(By.ID, "sFlagHistory")
        raw_history = history_element.get_attribute("textContent").strip()

        # Clean flag history
        flag_history = " | ".join(
            [line.strip() for line in raw_history.split("\n") if line.strip()]
        )
        change_count = flag_history.lower().count("effective")

        # 2. Registered Owner
        owner = driver.find_element(By.ID, "sRegOwnerCur").text.strip()

        # 3. Sanctions
        try:
            ship_sanction = driver.find_element(
                By.XPATH,
                "//td[span[contains(text(), 'Ship UN Sanction')]]/following-sibling::td",
            ).text.strip()
        except:
            ship_sanction = "N/A"

        try:
            entity_sanction = driver.find_element(
                By.XPATH,
                "//td[span[contains(text(), 'Owning/operating entity')]]/following-sibling::td",
            ).text.strip()
        except:
            entity_sanction = "N/A"

        return {
            "Input_IMO": input_imo,
            "Name": ship_name,
            "Current_Flag": current_flag,
            "Flag_History": flag_history,
            "Flag_Change_Count": change_count,
            "Owner": owner,
            "Ship_UN_Sanction": ship_sanction,
            "Entity_UN_Sanction": entity_sanction,
        }
    except Exception as e:
        print(f"Error scraping data for IMO {input_imo}: {e}")
        return None


# 3. Main Loop
for imo in imo_list:
    try:
        print(f"Searching for IMO: {imo}")
        driver.get("https://gisis.imo.org/Public/SHIPS/Default.aspx")

        wait = WebDriverWait(driver, 10)
        search_box = wait.until(
            EC.presence_of_element_located(
                (By.ID, "ctl00_bodyPlaceHolder_Default_tbxShipImoNumber")
            )
        )

        search_box.clear()
        search_box.send_keys(str(imo))
        search_box.send_keys(Keys.ENTER)

        # Check if results exist
        try:
            result_row = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".gridviewer_row"))
            )
            result_row.click()
        except:
            print(f"No results found for IMO: {imo}")
            continue

        # Scrape
        ship_info = scrape_particulars(imo)
        if ship_info:
            results_data.append(ship_info)
            print(f"Saved data for {ship_info['Name']} ({ship_info['Current_Flag']})")

            # Save to CSV every cycle
            pd.DataFrame(results_data).to_csv("imo_detailed_results.csv", index=False)

    except Exception as e:
        print(f"General error on IMO {imo}: {e}")
        continue

print("Pipeline complete.")
