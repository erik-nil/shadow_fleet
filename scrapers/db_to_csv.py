import sqlite3
import pandas as pd


def export_ships_to_csv():
    database_name = "scrapers/suspect_vessels_more_data.db"
    output_filename = "scrapers/suspect_vessels_more_data.csv"

    # Skapa anslutning
    conn = sqlite3.connect(database_name)

    try:
        # SQL-fråga som hämtar allt från din tabell
        # Vi sorterar så att de som är 'DONE' kommer först
        query = """
            SELECT 
                imo, 
                ism_name, ism_imo, ism_address, 
                owner_name, owner_imo, owner_address, 
                commercial_name, commercial_imo, commercial_address 
            FROM ships 
            WHERE status = 'DONE'
        """

        # Läs in i Pandas
        df = pd.read_sql_query(query, conn)

        # Spara till CSV
        # utf-8-sig används för att Excel ska hantera adresser med specialtecken korrekt
        df.to_csv(output_filename, index=False, encoding="utf-8-sig")

        print(f"Export lyckades!")
        print(f"Fil sparad: {output_filename}")
        print(f"Totalt antal rader: {len(df)}")
        print(f"Antal klara fartyg: {len(df[df['status'] == 'DONE'])}")

    except Exception as e:
        print(f"Ett fel uppstod: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    export_ships_to_csv()
