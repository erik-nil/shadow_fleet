"""
import pandas as pd

# Filnamn
VESSELS_FILE = "vessels.csv"
SHADOW_FILE = "shadow_fleet.csv"
OUTPUT_FILE = "matched_vessels.csv"


def clean_imo(val):
    #Hjälpfunktion för att städa IMO-nummer till rena strängar (t.ex. '9282041')
    try:
        # Gör om till float först för att hantera "9282041.0", sen int, sen sträng
        return str(int(float(val)))
    except:
        return str(val).strip()


def main():
    print("Läser in filer...")

    # 1. Läs in Shadow Fleet-listan (bara IMO-kolumnen behövs egentligen)
    try:
        shadow_df = pd.read_csv(SHADOW_FILE)
        # Skapa en 'set' av alla IMO-nummer vi letar efter (mycket snabbare sökning)
        target_imos = set(shadow_df["IMO"].apply(clean_imo))
        print(f"Hittade {len(target_imos)} unika IMO-nummer i {SHADOW_FILE}.")
    except Exception as e:
        print(f"Fel vid inläsning av {SHADOW_FILE}: {e}")
        return

    # 2. Läs in Vessels-filen
    try:
        vessels_df = pd.read_csv(VESSELS_FILE)
        # Spara originalantalet rader
        original_count = len(vessels_df)
    except Exception as e:
        print(f"Fel vid inläsning av {VESSELS_FILE}: {e}")
        return

    # 3. Filtrera: Behåll bara rader där IMO finns i target_imos
    # Vi skapar en temporär kolumn för matchning för att inte ändra originaldatan
    vessels_df["clean_imo"] = vessels_df["IMO"].apply(clean_imo)

    matched_df = vessels_df[vessels_df["clean_imo"].isin(target_imos)]

    # Ta bort hjälpkolumnen igen
    matched_df = matched_df.drop(columns=["clean_imo"])

    # 4. Spara resultatet
    matched_df.to_csv(OUTPUT_FILE, index=False)

    print("-" * 30)
    print(f"Klar! Filtrering slutförd.")
    print(f"Originalrader i vessels.csv: {original_count}")
    print(f"Matchade rader (Shadow Fleet): {len(matched_df)}")
    print(f"Resultat sparat till: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
"""

import pandas as pd

# Filnamn
VESSELS_FILE = "vessels.csv"
SHADOW_FILE = "shadow_fleet.csv"
CLEAN_CANDIDATES_FILE = "unknown_vessels.csv"


def clean_imo(val):
    """Säkerställer att IMO-nummer matchar oavsett format (int/float/str)"""
    try:
        return str(int(float(val)))
    except:
        return str(val).strip()


def main():
    print("Startar rensning av vessels.csv...")

    # 1. Läs in Shadow Fleet-listan (dina 600 bekräftade)
    shadow_df = pd.read_csv(SHADOW_FILE)
    confirmed_imos = set(shadow_df["IMO"].apply(clean_imo))
    print(f"Hittade {len(confirmed_imos)} kända shadow-fartyg.")

    # 2. Läs in alla vessels
    vessels_df = pd.read_csv(VESSELS_FILE)
    original_count = len(vessels_df)

    # 3. Filtrera bort de kända fartygen
    # Vi behåller bara rader där IMO-numret INTE finns i confirmed_imos
    vessels_df["tmp_imo"] = vessels_df["IMO"].apply(clean_imo)
    unknown_vessels_df = vessels_df[~vessels_df["tmp_imo"].isin(confirmed_imos)].copy()

    # Ta bort hjälpkolumnen
    unknown_vessels_df = unknown_vessels_df.drop(columns=["tmp_imo"])

    # 4. Spara den nya listan med okända fartyg
    unknown_vessels_df.to_csv(CLEAN_CANDIDATES_FILE, index=False)

    print("-" * 30)
    print(f"Rensning klar!")
    print(f"Antal fartyg från början: {original_count}")
    print(f"Antal borttagna (kända): {original_count - len(unknown_vessels_df)}")
    print(f"Antal kvarvarande okända: {len(unknown_vessels_df)}")
    print(f"Resultat sparat till: {CLEAN_CANDIDATES_FILE}")


if __name__ == "__main__":
    main()
