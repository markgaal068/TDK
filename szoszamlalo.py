import pandas as pd
from collections import Counter
import re

def count_words_in_excel(input_excel, output_file=None):
    # Excel beolvasása
    try:
        df = pd.read_excel(input_excel)
    except Exception as e:
        print(f"Hiba az Excel fájl beolvasásakor: {e}")
        return

    # Ellenőrizzük, hogy van-e második oszlop
    if df.empty or df.shape[1] < 2:
        print("Az Excel fájlban nincs elég oszlop!")
        return

    # Második oszlop szövegének összegyűjtése
    column_name = df.columns[1]  # Második oszlop neve
    text_data = " ".join(df[column_name].dropna().astype(str))  # Összes szöveg összefűzése

    # Szavak kigyűjtése és gyakoriság számítás
    words = re.findall(r'\b\w+\b', text_data.lower())  # Szavak kigyűjtése (kisbetűkre váltva)
    word_counts = Counter(words)

    # 250 leggyakoribb szó kigyűjtése
    most_common_words = word_counts.most_common(550)

    # Eredmények kiíratása
    print("Leggyakoribb szavak és előfordulásuk száma:")
    for word, count in most_common_words:
        print(f"{word}: {count}")

    # Eredmények mentése fájlba (opcionális)
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Word,Count\n")
                for word, count in most_common_words:
                    f.write(f"{word};{count}\n")
            print(f"Eredmények mentve ide: {output_file}")
        except Exception as e:
            print(f"Hiba a fájl mentésekor: {e}")

# Példa fájlnevek
input_excel = "D:/Done.xlsx"  # Az elemzendő Excel fájl
output_file = "D:/word_countsFIN_550.csv"  # Opcionális: eredmény CSV fájl

# Futtatás
count_words_in_excel(input_excel, output_file)