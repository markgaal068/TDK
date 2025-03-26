import os
import re
import openpyxl
from pdfminer.high_level import extract_text as pdf_extract_text
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from bs4 import BeautifulSoup
from config import CONFIG
from utils.helpers import create_directory
from typing import List, Dict

class TextExtractor:
    def __init__(self):
        self.config = CONFIG
        self.output_file = self.config.get("extraction", {}).get("output_file", "output/results.xlsx")
        self.download_dir = self.config["system"]["temp_dir"]
        create_directory(os.path.dirname(self.output_file))
        create_directory(self.download_dir)

    def process_files(self):
        """Main processing method with enhanced error handling"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Extracted Content"
        headers = [
            "Filename", 
            "Content Preview", 
            "Keywords", 
            "Status"
        ]
        ws.append(headers)

        processed_count = 0
        for filename in os.listdir(self.download_dir):
            if filename.endswith(tuple(self.config["input"]["supported_formats"])):
                print(f"\nProcessing {filename}...")
                result = self.process_file(filename)
                
                ws.append([
                    filename,
                    result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"],
                    ", ".join(result["combined_keywords"][:10]),
                    result["status"]
                ])
                processed_count += 1
                print(f"Processed {filename} - Status: {result['status']}")

        if processed_count > 0:
            wb.save(self.output_file)
            print(f"\nSuccessfully processed {processed_count} files. Results saved to {self.output_file}")
        else:
            print("\nNo supported files found in the directory.")

    def extract_keywords_section(self, text: str) -> List[str]:
        """Kulcsszavak kinyerése a dedikált szekcióból"""
        try:
            strategy = self.config["processing"]["keywords"]["extraction"]
            keywords = []
            
            for marker in strategy["section_markers"]["start"]:
                start_pos = text.find(marker)
                if start_pos != -1:
                    start_pos += len(marker)
                    end_pos = len(text)
                    
                    for end_marker in strategy["section_markers"]["end"]:
                        pos = text.find(end_marker, start_pos)
                        if pos != -1 and pos < end_pos:
                            end_pos = pos
                    
                    section = text[start_pos:end_pos].strip()
                    keywords.extend(self.clean_keywords(section))
                    break
                    
            return list(set(keywords))[:10]
        except Exception as e:
            print(f"Hiba a kulcsszó szekció kinyerésekor: {e}")
            return []

    def process_file(self, filename: str) -> Dict:
        """Process individual file with robust error handling"""
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            if filename.lower().endswith('.pdf'):
                text = self.extract_pdf_text(filepath)
            elif filename.lower().endswith('.docx'):
                text = self.extract_docx_text(filepath)
            else:
                text = self.extract_plain_text(filepath)

            content = self.extract_main_content(text)
            keywords = self.extract_keywords(text)
            
            return {
                "filename": filename,
                "content": content,
                "combined_keywords": keywords,
                "status": "Success"
            }

        except Exception as e:
            return {
                "filename": filename,
                "content": "",
                "combined_keywords": [],
                "status": f"Error: {str(e)}"
            }

    def extract_pdf_text(self, filepath: str) -> str:
        """Extract text from PDF with proper error handling"""
        try:
            return pdf_extract_text(filepath)
        except PDFTextExtractionNotAllowed:
            raise Exception("PDF doesn't allow text extraction")
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    def extract_docx_text(self, filepath: str) -> str:
        """Extract text from DOCX files"""
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"DOCX processing failed: {str(e)}")

    def extract_plain_text(self, filepath: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise Exception(f"Text file decoding failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Text file reading failed: {str(e)}")

    def extract_main_content(self, text: str) -> str:
        """Extract main content with improved section detection"""
        # Common section headers
        start_markers = ["Introduction", "INTRODUCTION", "Bevezetés", "Abstract", "ABSTRACT"]
        end_markers = ["References:", "REFERENCES", "Irodalomjegyzék"]
        
        # Find the first matching header
        start_pos = 0
        for marker in start_markers:
            pos = text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                break
                
        # Find the first reference section after our content
        end_pos = len(text)
        for marker in end_markers:
            pos = text.find(marker, start_pos)
            if pos != -1 and pos < end_pos:
                end_pos = pos
                
        return text[start_pos:end_pos].strip()

    def extract_keywords(self, text: str) -> List[str]:
        """Combine all keyword extraction methods"""
        section_keywords = self.extract_keywords_section(text)
        text_keywords = self.extract_keywords_from_text(text)
        return self.combine_keywords(section_keywords, text_keywords)

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from the main text using basic NLP techniques"""
        # Remove common words and punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'])
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequencies
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 most frequent words
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    def clean_keywords(self, text: str) -> List[str]:
        """Clean and normalize keywords"""
        # Split by common separators
        keywords = re.split(r'[,;]', text)
        # Clean each keyword
        cleaned = []
        for keyword in keywords:
            # Remove extra whitespace and convert to lowercase
            cleaned_keyword = keyword.strip().lower()
            # Remove special characters but keep spaces
            cleaned_keyword = re.sub(r'[^\w\s]', '', cleaned_keyword)
            if cleaned_keyword:
                cleaned.append(cleaned_keyword)
        return cleaned

    def combine_keywords(self, section_keywords: List[str], text_keywords: List[str]) -> List[str]:
        """Combine keywords from different sources and remove duplicates"""
        combined = set(section_keywords)
        combined.update([word for word, _ in text_keywords])
        return list(combined)[:10]  # Keep top 10 keywords

if __name__ == "__main__":
    try:
        extractor = TextExtractor()
        extractor.process_files()
    except Exception as e:
        print(f"Fatal error: {str(e)}")