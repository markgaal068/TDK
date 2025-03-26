import pandas as pd

# Bemeneti és kimeneti fájlok neve
input_file = "D:/AllAbstracts_Cleaned_v2.csv"
output_file = "D:/output.csv"

# CSV fájl beolvasása
df = pd.read_csv(input_file)

# Kettőspont és az utána lévő szóköz eltávolítása minden cellából
df = df.applymap(lambda x: x.replace(": ", "") if isinstance(x, str) else x)

# Javított adatok mentése új CSV fájlba
df.to_csv(output_file, index=False)