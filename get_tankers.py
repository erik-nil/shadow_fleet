import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

# 1. Connect to your existing Chrome
# Open chrome with this line "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp_chrome"
# go to localhost:9222
# start this python program
# navigate to vesselfinder
# start to scrape
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

all_vessels = []
CSV_FILENAME = "vesselfinder_tankers_full.csv"

# 2. Set your range
start_page = int(input("Enter the page number you are currently on: "))
end_page = int(input("Enter the page number to stop at: "))

try:
    for p in range(start_page, end_page + 1):
        url = f"https://www.vesselfinder.com/vessels?page={p}&type=6"
        print(f"--- Navigating to Page {p} ---")
        driver.get(url)

        # --- IMPROVEMENT 1: AUTO-SCROLL TO BOTTOM ---
        print("Scrolling to load all data...")
        # Scroll down in increments to trigger lazy-loading
        for i in range(1, 5):
            driver.execute_script(
                f"window.scrollTo(0, document.body.scrollHeight * {i/4});"
            )
            time.sleep(0.5)
        time.sleep(1)  # Final stabilization

        if "Verify you are human" in driver.page_source:
            input("Captcha detected! Solve it in the browser, then press ENTER here...")

        # 3. Scrape the rows
        rows = driver.find_elements(
            By.XPATH, "//tr[descendant::a[contains(@class, 'ship-link')]]"
        )

        for row in rows:
            try:
                link_element = row.find_element(By.CLASS_NAME, "ship-link")
                ship_url = link_element.get_attribute("href")
                imo = ship_url.split("/")[-1] if ship_url else "N/A"

                # --- IMPROVEMENT 2: EXTRACT FLAG (COUNTRY) ---
                # The flag name is stored in the 'title' attribute of the flag-icon div
                try:
                    flag_element = row.find_element(By.CLASS_NAME, "flag-icon")
                    flag_land = flag_element.get_attribute("title")
                except:
                    flag_land = "Unknown"

                all_vessels.append(
                    {
                        "IMO": imo,
                        "Name": row.find_element(By.CLASS_NAME, "slna").text.strip(),
                        "Type": row.find_element(By.CLASS_NAME, "slty").text.strip(),
                        "Flag": flag_land,
                        "Built": row.find_element(By.CLASS_NAME, "v3").text.strip(),
                        "GT": row.find_element(By.CLASS_NAME, "v4").text.strip(),
                        "DWT": row.find_element(By.CLASS_NAME, "v5").text.strip(),
                        "Size": row.find_element(By.CLASS_NAME, "v6").text.strip(),
                    }
                )
            except:
                continue

        print(f"Successfully scraped page {p}. Total ships: {len(all_vessels)}")

        if p % 5 == 0:
            pd.DataFrame(all_vessels).drop_duplicates(subset=["IMO"]).to_csv(
                CSV_FILENAME, index=False
            )
            print("--- Progress saved to CSV ---")

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    if all_vessels:
        df = pd.DataFrame(all_vessels).drop_duplicates(subset=["IMO"])
        df.to_csv(CSV_FILENAME, index=False)
        print(f"Finished. Total unique ships saved: {len(df)}")
