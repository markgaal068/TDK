import os
import re
import openpyxl
from pdfminer.high_level import extract_text as pdf_extract_text
from bs4 import BeautifulSoup
from config import CONFIG
from utils.helpers import create_directory
from typing import List, Tuple, Dict

class TextExtractor:
    def __init__(self):
        self.config = CONFIG
        create_directory(os.path.dirname(self.config["extraction"]["output_file"]))

    def process_files(self):
        """Main processing method"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Extracted Content"
        ws.append([
            "Issue", 
            "Content", 
            "Keywords from Section", 
            "Keywords from Text",
            "Combined Keywords",
            "Status"
        ])

        for filename in os.listdir(self.config["download"]["output_dir"]):
            if filename.endswith(tuple(self.config["extraction"]["supported_formats"])):
                result = self.process_file(filename)
                ws.append([
                    result["issue"],
                    result["content"],
                    ", ".join(result["keywords_section"]),
                    ", ".join(result["keywords_text"]),
                    ", ".join(result["combined_keywords"]),
                    result["status"]
                ])

        wb.save(self.config["extraction"]["output_file"])
        print(f"Extraction complete. Results saved to {self.config['extraction']['output_file']}")

    def process_file(self, filename: str) -> Dict:
        """Process individual file"""
        filepath = os.path.join(self.config["download"]["output_dir"], filename)
        issue_num = os.path.splitext(filename)[0]
        
        try:
            # Extract raw text based on file type
            if filename.endswith('.pdf'):
                text = pdf_extract_text(filepath)
            elif filename.endswith('.html'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text = soup.get_text()
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()

            # Process the extracted text
            content = self.extract_main_content(text)
            keywords_section = self.extract_keywords_section(text)
            keywords_text = self.extract_keywords_from_text(text)
            
            # Combine and score keywords
            combined = self.combine_keywords(keywords_section, keywords_text)

            return {
                "issue": issue_num,
                "content": content,
                "keywords_section": keywords_section,
                "keywords_text": keywords_text,
                "combined_keywords": combined,
                "status": "Success"
            }

        except Exception as e:
            return {
                "issue": issue_num,
                "content": "",
                "keywords_section": [],
                "keywords_text": [],
                "combined_keywords": [],
                "status": f"Error: {str(e)}"
            }

    def extract_main_content(self, text: str) -> str:
        """Extract main content between abstract and references"""
        start_markers = ["Abstract:", "ABSTRACT", "Összefoglalás:"]
        end_markers = ["References:", "REFERENCES", "Irodalomjegyzék"]
        
        start_pos = -1
        for marker in start_markers:
            pos = text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                break
                
        end_pos = len(text)
        for marker in end_markers:
            pos = text.find(marker)
            if pos != -1 and pos < end_pos:
                end_pos = pos
                
        return text[start_pos:end_pos].strip() if start_pos != -1 else text

    def extract_keywords_section(self, text: str) -> List[str]:
        """Extract keywords from dedicated section"""
        strategy = self.config["extraction"]["strategies"]["from_keywords_section"]
        keywords = []
        
        for marker in strategy["start_markers"]:
            start_pos = text.find(marker)
            if start_pos != -1:
                start_pos += len(marker)
                end_pos = len(text)
                
                for end_marker in strategy["end_markers"]:
                    pos = text.find(end_marker, start_pos)
                    if pos != -1 and pos < end_pos:
                        end_pos = pos
                
                section = text[start_pos:end_pos].strip()
                keywords.extend(self.clean_keywords(section))
                break
                
        return list(set(keywords))  # Remove duplicates

    def extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from full text"""
        if not self.config["extraction"]["strategies"]["from_full_text"]["enabled"]:
            return []
            
        strategy = self.config["extraction"]["strategies"]["from_full_text"]
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Get combined stopwords
        stopwords = (self.config["cleaning"]["stopwords"]["english"] + 
                    self.config["cleaning"]["stopwords"]["hungarian"])
        
        # Filter and process words
        keywords = [
            word for word in words
            if (len(word) >= strategy["min_word_length"] and
                word not in stopwords and
                (not strategy["exclude_numbers"] or not word.isdigit()))
        ]
        
        # Count and get most frequent
        word_counts = {}
        for word in keywords:
            word_counts[word] = word_counts.get(word, 0) + 1
            
        return sorted(word_counts.keys(), 
                     key=lambda x: word_counts[x], 
                     reverse=True)[:strategy["max_words"]]

    def clean_keywords(self, keywords_text: str) -> List[str]:
        """Clean and normalize keywords"""
        keywords = []
        for part in keywords_text.split(','):
            part = part.strip()
            if ';' in part:
                keywords.extend(p.strip() for p in part.split(';'))
            elif ' ' in part and len(part) > 15:  # Probably not a single keyword
                continue
            else:
                keywords.append(part)
        return [kw.lower() for kw in keywords if kw]

    def combine_keywords(self, section_kws: List[str], text_kws: List[str]) -> List[str]:
        """Combine and score keywords from different sources"""
        scoring = self.config["analysis"]["scoring"]
        combined = {}
        
        # Add keywords from section with higher weight
        for kw in section_kws:
            combined[kw] = combined.get(kw, 0) + scoring["keywords_section_weight"]
        
        # Add keywords from text with normal weight
        for kw in text_kws:
            combined[kw] = combined.get(kw, 0) + scoring["full_text_weight"]
        
        return sorted(combined.keys(), key=lambda x: combined[x], reverse=True)

if __name__ == "__main__":
    extractor = TextExtractor()
    extractor.process_files()