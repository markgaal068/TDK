import pandas as pd
from nltk.corpus import stopwords
from collections import Counter
import nltk

nltk.download('stopwords')

def clean_text_from_stopwords(input_excel, output_excel):
    # Magyar és angol stop wordök beállítása
    stop_words = stopwords.words('english')
    stop_word_counter = Counter()

    # Excel beolvasása
    try:
        df = pd.read_excel(input_excel)
    except Exception as e:
        print(f"Hiba az Excel fájl beolvasásakor: {e}")
        return

    # Feltételezzük, hogy a szöveg a második oszlopban van
    if df.empty or df.shape[1] < 2:
        print("Az Excel fájlban nincs elég oszlop!")
        return

    column_name = df.columns[1]  # Második oszlop neve
    df['Cleaned_Text'] = df[column_name].apply(lambda text: clean_and_count_stopwords(text, stop_words, stop_word_counter))

    # Stop word statisztikák kiíratása
    print("Eltávolított stop wordök száma:")
    for word, count in stop_word_counter.most_common():
        print(f"{word}: {count}")

    # Új fájl mentése
    try:
        df.to_excel(output_excel, index=False)
        print(f"Megtisztított szöveg mentve ide: {output_excel}")
    except Exception as e:
        print(f"Hiba a fájl mentésekor: {e}")

def clean_and_count_stopwords(text, stop_words, counter):
    """Eltávolítja a stop wordöket a szövegből és számolja őket."""
    if not isinstance(text, str):
        return text  # Ha nem szöveg, hagyjuk érintetlenül

    words = text.split()
    cleaned_words = []

    for word in words:
        if word.lower() in stop_words:
            counter[word.lower()] += 1
        else:
            cleaned_words.append(word)

    return " ".join(cleaned_words)

input_excel = "D:/Input.xlsx"  # Az eredeti Excel fájl neve
output_excel = "output_cleaned.xlsx"  # A megtisztított Excel fájl neve

clean_text_from_stopwords(input_excel, output_excel)