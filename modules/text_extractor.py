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
        create_directory(self.download_dir)  # Ensure download directory exists

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

    def process_file(self, filename: str) -> Dict:
        """Process individual file with robust error handling"""
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = self.extract_pdf_text(filepath)
            elif filename.lower().endswith(('.html', '.htm')):
                text = self.extract_html_text(filepath)
            else:
                text = self.extract_plain_text(filepath)

            # Process the extracted text
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

    def extract_html_text(self, filepath: str) -> str:
        """Extract text from HTML files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            raise Exception(f"HTML processing failed: {str(e)}")

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
        # Use the headers from config
        start_markers = self.config["processing"]["sections"]["common_headers"]
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

    # ... [rest of the methods remain the same as in previous implementation]

if __name__ == "__main__":
    try:
        extractor = TextExtractor()
        extractor.process_files()
    except Exception as e:
        print(f"Fatal error: {str(e)}")