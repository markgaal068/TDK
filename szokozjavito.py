import pandas as pd
import re

def fix_spacing_in_words(text):
    if pd.isna(text):
        return text
    # Csak azokat a szavakat javítja, amelyek hibásak (pl. "k o d"), de az önálló "a" marad.
    fixed_text = re.sub(r'\b([a-zA-Záéíóöőúüű])(?:\s+([a-zA-Záéíóöőúüű]))+\b',
                        lambda m: m.group(0).replace(" ", ""), text)
    return fixed_text

# Beolvasás
input_file = "D:/AllAbstracts_Cleaned.xlsx"  # Az eredeti fájl neve
output_file = "D:/output_fixed.xlsx"  # A javított fájl neve

# Excel fájl beolvasása pandas DataFrame-be
df = pd.read_excel(input_file)

# Minden cella javítása az adott oszlopokban
df = df.applymap(fix_spacing_in_words)

# Javított fájl mentése
df.to_excel(output_file, index=False)

print(f"A javított fájl elmentve: {output_file}")