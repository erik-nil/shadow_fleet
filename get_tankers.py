# %%

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Load the file specifically as a DataFrame
file_path = r"C:\Users\erik_\OneDrive\Skrivbord\Akademisk Comeback 25\Python_linc\Project\shadow_fleet\shadow_fleet_df.csv"
shadow_fleet_df = pd.read_csv(file_path)
shadow_fleet_df.set_index("IMO", inplace=True)

# %%
chrome_options = Options()
extension_path = r"C:\Users\erik_\OneDrive\Skrivbord\Akademisk Comeback 25\Python_linc\Project\shadow_fleet\adblock.crx"
chrome_options.add_extension(extension_path)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.marinevesseltraffic.com/ship-owner-manager-ism-data")

try:
    # Wait up to 10 seconds for the "Consent" text to appear and be clickable
    consent_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//p[text()='Consent']"))
    )
    consent_button.click()
    print("Cookies accepted.")
except Exception as e:
    print("Consent button not found or already closed:", e)

# Find the search box
for imo in shadow_fleet_df.index:
    # 1. Locate the search box
    search_box = driver.find_element(By.ID, "search-main")  # Note: use 'ID' in caps

    # 2. Clear previous entry (important for consecutive searches!)
    search_box.clear()

    # 3. Enter IMO and hit Enter
    search_box.send_keys(str(imo) + Keys.ENTER)

    # 4. Optional: Add a small wait for the page to load
    time.sleep(20)

# %%
