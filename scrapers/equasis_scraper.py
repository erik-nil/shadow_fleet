import sqlite3
import pandas as pd
import time
import random
import winsound  # För ljudsignaler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- KONFIGURATION ---
DB_FILE = "scrapers/shadow_fleet_scrape.db"
INPUT_CSV = "shadow_fleet_imo_names.csv"
CHROME_PORT = "127.0.0.1:9222"


# 1. Koppla upp mot databasen
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Skapa tabell om den inte finns
    c.execute(
        """CREATE TABLE IF NOT EXISTS ships (
                    imo TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'PENDING',
                    ism_name TEXT, ism_imo TEXT, ism_address TEXT,
                    owner_name TEXT, owner_imo TEXT, owner_address TEXT,
                    commercial_name TEXT, commercial_imo TEXT, commercial_address TEXT
                )"""
    )
    conn.commit()
    return conn


# 2. Importera CSV till Databasen (Körs bara om databasen är tom)
def import_csv_to_db(conn):
    c = conn.cursor()
    c.execute("SELECT count(*) FROM ships")
    if c.fetchone()[0] == 0:
        print("Importerar CSV till databasen...")
        df = pd.read_csv(INPUT_CSV)
        # Antar att kolumnen heter 'IMO' i din CSV
        for imo in df["IMO"].unique():
            c.execute("INSERT OR IGNORE INTO ships (imo) VALUES (?)", (str(imo),))
        conn.commit()
        print("Import klar.")


# 3. Navigera säkert (JavaScript Injection)
def go_to_ship(driver, imo):
    try:
        # Detta är Equasis interna sökkommando
        script = f"document.formShip.P_IMO.value='{imo}';document.formShip.submit();"
        driver.execute_script(script)
        # Vänta på att sidan laddar (t.ex. leta efter 'Ship Particulars' eller felmeddelande)
        time.sleep(random.uniform(1, 4))  # Vänta lite för att låta sidan börja ladda
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "blocLSMobile"))
        )
        return True
    except Exception as e:
        print(f"Kunde inte navigera till {imo}. Är du inloggad?")
        return False


# 4. Extrahera Data (Samma logik som förut, men returnerar en dictionary)
def scrape_data(driver):
    data = {}
    blocks = driver.find_elements(By.CLASS_NAME, "blocLSMobile")
    for block in blocks:
        try:
            txt = block.get_attribute("textContent")
            name = (
                block.find_element(By.TAG_NAME, "h3")
                .get_attribute("textContent")
                .strip()
            )

            # Identifiera vilken roll detta block är
            role_prefix = ""
            if "ism manager" in txt.lower():
                role_prefix = "ism"
            elif "registered owner" in txt.lower():
                role_prefix = "owner"
            elif "commercial manager" in txt.lower():
                role_prefix = "commercial"
            else:
                continue  # Hoppa över okända roller

            # Hämta värden
            # Här använder vi en förenklad logik för att spara kodutrymme
            # Du kan klistra in din avancerade extraktor här om du vill
            values = block.find_elements(By.CLASS_NAME, "valeur")
            if len(values) >= 3:
                data[f"{role_prefix}_name"] = name
                data[f"{role_prefix}_imo"] = (
                    values[0].get_attribute("textContent").strip()
                )
                data[f"{role_prefix}_address"] = (
                    values[2].get_attribute("textContent").strip()
                )
        except:
            continue
    return data


# --- HUVUDPROGRAM ---
def main():
    conn = init_db()
    import_csv_to_db(conn)

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", CHROME_PORT)
    driver = webdriver.Chrome(options=chrome_options)

    print("--- Startar Automatisk Bearbetning ---")

    while True:
        # 1. Hämta nästa skepp
        c = conn.cursor()
        c.execute("SELECT imo FROM ships WHERE status='PENDING' LIMIT 1")
        row = c.fetchone()

        if not row:
            print("Alla skepp är klara!")
            break

        imo = row[0]
        print(f"Bearbetar IMO {imo}...", end="")

        # 2. Navigera till skeppet
        success = go_to_ship(driver, imo)

        if not success:
            winsound.Beep(1000, 1000)
            input("\n[PAUS] Utloggad? Logga in och tryck ENTER...")
            continue

        # 3. Skrapa datan
        data = scrape_data(driver)

        # 4. Spara till databas
        if data:
            columns = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append("DONE")
            values.append(imo)

            sql = f"UPDATE ships SET {columns}, status = ? WHERE imo = ?"
            c.execute(sql, values)
            conn.commit()
            print(" KLAR.")
        else:
            c.execute("UPDATE ships SET status='NO_DATA' WHERE imo=?", (imo,))
            conn.commit()
            print(" INGEN DATA.")

        # 5. Gå tillbaka till sökfältet
        driver.back()

        # 6. Viktigt: Vänta lite så att sökssidan hinner ladda innan nästa JS-injektion
        # Slumpmässig tid (human-like)
        sleep_time = random.uniform(2.5, 5.5)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
