import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from textblob import TextBlob
import re
import string
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
import PyPDF2
import requests
from urllib.parse import urlparse
import os

# NLTK adatok letöltése
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Stop words lista
stop_words = set(stopwords.words('english'))

class TextAnalyzer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        
        # Kisbetűsítés
        text = text.lower()
        
        # Speciális karakterek eltávolítása
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Extra szóközök eltávolítása
        text = ' '.join(text.split())
        
        return text

    def remove_stopwords(self, text):
        words = text.split()
        filtered_words = [word for word in words if word not in stop_words]
        return ' '.join(filtered_words)

    def process_text(self, text):
        if not isinstance(text, str):
            return ""
        
        # Szöveg tisztítása
        text = self.clean_text(text)
        
        # Stop words eltávolítása
        text = self.remove_stopwords(text)
        
        # Egyesszámú alakokra alakítás
        words = []
        for word in text.split():
            try:
                singular_word = self.lemmatizer.lemmatize(word, pos='n')  
                words.append(singular_word)
            except UnicodeDecodeError:
                words.append("_")  
            except Exception as e:
                print(f"Error with word '{word}': {e}")
                words.append(word)  
        return ' '.join(words)

    def get_keywords(self, text, top_n=5):
        words = text.split()
        word_freq = Counter(words)
        return ', '.join([word for word, _ in word_freq.most_common(top_n)])

    def get_sentiment(self, text):
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def get_entities(self, text):
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        named_entities = ne_chunk(pos_tags)
        
        entities = {}
        for chunk in named_entities:
            if hasattr(chunk, 'label'):
                entity_type = chunk.label()
                entity_text = ' '.join([token for token, pos in chunk])
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append(entity_text)
        return entities

    def get_pos_stats(self, text):
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        pos_counts = Counter(tag for word, tag in pos_tags)
        return dict(pos_counts)

    def get_readability_score(self, text):
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        if not sentences:
            return 0
        avg_sentence_length = len(words) / len(sentences)
        return 100 - (avg_sentence_length * 10)

    def generate_wordcloud(self, text, output_file='wordcloud.png'):
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(output_file)
        plt.close()

    def get_tfidf_keywords(self, texts, top_n=5):
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Átlagos TF-IDF értékek számítása
        avg_tfidf = np.array(tfidf_matrix.mean(axis=0)).flatten()
        
        # Top kulcsszavak kiválasztása
        top_indices = avg_tfidf.argsort()[-top_n:][::-1]
        return [feature_names[i] for i in top_indices]

def extract_abstract_from_pdf(pdf_path):
    """Extract abstract from PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # Abstract extraction logic
            abstract_pattern = r'abstract\s*(.*?)(?=\n\n|\Z)'
            abstract_match = re.search(abstract_pattern, text, re.IGNORECASE | re.DOTALL)
            
            if abstract_match:
                return abstract_match.group(1).strip()
            else:
                return text[:500]  # Return first 500 characters if no abstract found
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return ""

def download_pdf_from_url(url, output_dir="downloads"):
    """Download PDF from URL."""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(output_dir, os.path.basename(urlparse(url).path))
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
                
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            print(f"Error downloading PDF from {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading PDF from {url}: {e}")
        return None

def process_pdfs(pdf_files, output_file="abstracts.xlsx"):
    """Process multiple PDF files and extract abstracts."""
    analyzer = TextAnalyzer()
    results = []
    
    for pdf_file in pdf_files:
        try:
            # Extract abstract
            abstract = extract_abstract_from_pdf(pdf_file)
            
            # Process text
            cleaned_text = analyzer.clean_text(abstract)
            no_stopwords = analyzer.remove_stopwords(cleaned_text)
            singularized = analyzer.process_text(no_stopwords)
            
            # Get additional information
            keywords = analyzer.get_keywords(singularized)
            sentiment = analyzer.get_sentiment(abstract)
            readability = analyzer.get_readability_score(abstract)
            
            # Add to results
            results.append({
                'File_Name': os.path.basename(pdf_file),
                'Original_Abstract': abstract,
                'Cleaned_Text': cleaned_text,
                'No_Stopwords': no_stopwords,
                'Singularized': singularized,
                'Keywords': keywords,
                'Sentiment': sentiment,
                'Readability': readability,
                'Processed_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            continue
    
    # Create DataFrame and save to Excel
    if results:
        df = pd.DataFrame(results)
        
        # Save to Excel with formatting
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Abstracts')
            
            # Get the workbook and the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Abstracts']
            
            # Format column widths
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        print(f"Results saved to {output_file}")
        return True
    else:
        print("No results to save")
        return False

def process_urls(urls, output_file="abstracts.xlsx"):
    """Process PDFs from URLs."""
    pdf_files = []
    
    for url in urls:
        pdf_file = download_pdf_from_url(url)
        if pdf_file:
            pdf_files.append(pdf_file)
    
    if pdf_files:
        return process_pdfs(pdf_files, output_file)
    else:
        print("No PDFs were successfully downloaded")
        return False

def process_text(text):
    """
    Standalone function to process text using TextAnalyzer.
    This function is provided for backward compatibility and simpler usage.
    """
    analyzer = TextAnalyzer()
    return analyzer.process_text(text)

if __name__ == "__main__":
    # Example usage
    # Process local PDF files
    pdf_files = ["path/to/pdf1.pdf", "path/to/pdf2.pdf"]
    process_pdfs(pdf_files, "abstracts.xlsx")
    
    # Process PDFs from URLs
    urls = ["http://example.com/paper1.pdf", "http://example.com/paper2.pdf"]
    process_urls(urls, "abstracts_from_urls.xlsx")