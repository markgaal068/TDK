import openpyxl
import re
from config import CONFIG
from utils.helpers import create_directory
import os
from typing import List, Set, Optional

def clean_data():
    """
    Enhanced data cleaning functionality with:
    - Better stopword handling
    - Improved keyword extraction
    - Robust error handling
    - Config validation
    - Progress reporting
    """
    try:
        # Validate and get configuration with defaults
        config_cleaning = CONFIG.get("cleaning", {})
        config_merging = CONFIG.get("merging", {})
        
        input_file = config_merging.get("output_file", "output/merged_data.xlsx")
        output_file = config_cleaning.get("output_file", "output/cleaned_data.xlsx")
        stopwords = set(config_cleaning.get("stopwords", []))
        min_keyword_length = config_cleaning.get("min_keyword_length", 4)
        
        # Create output directory if needed
        create_directory(os.path.dirname(output_file))
        
        print("Loading workbook...")
        try:
            wb = openpyxl.load_workbook(input_file)
            ws = wb.active
        except FileNotFoundError:
            raise Exception(f"Input file not found: {input_file}")
        except Exception as e:
            raise Exception(f"Error loading workbook: {str(e)}")

        # Validate worksheet structure
        if ws.max_row < 2:
            print("No data found to clean (empty worksheet).")
            return
            
        # Add new columns for cleaned data if they don't exist
        if ws.cell(row=1, column=4).value != "Cleaned Content":
            ws.cell(row=1, column=4, value="Cleaned Content")
        if ws.cell(row=1, column=5).value != "Keywords":
            ws.cell(row=1, column=5, value="Keywords")
        
        print(f"Processing {ws.max_row - 1} rows...")
        processed_rows = 0
        
        for row in range(2, ws.max_row + 1):
            content = ws.cell(row=row, column=2).value
            if not content:
                continue
                
            try:
                # Clean and normalize content
                cleaned_content = clean_text(content, stopwords)
                
                # Extract keywords
                keywords = extract_keywords(cleaned_content, stopwords, min_keyword_length)
                
                # Update cells
                ws.cell(row=row, column=4, value=cleaned_content)
                ws.cell(row=row, column=5, value=", ".join(keywords))
                
                processed_rows += 1
                if processed_rows % 100 == 0:
                    print(f"Processed {processed_rows} rows...")
                    
            except Exception as e:
                print(f"Error processing row {row}: {str(e)}")
                continue
        
        # Sort data
        print("Sorting data...")
        sort_worksheet(ws)
        
        # Save results
        print("Saving results...")
        wb.save(output_file)
        print(f"Successfully cleaned and saved {processed_rows} rows to {output_file}")
        
    except Exception as e:
        print(f"Error in clean_data: {str(e)}")

def clean_text(text: str, stopwords: Set[str]) -> str:
    """Clean and normalize text content"""
    # Remove special characters and normalize whitespace
    cleaned = re.sub(r'[^\w\s]', ' ', str(text))
    # Remove stopwords and short words
    words = [
        word.lower() for word in re.findall(r'\b\w+\b', cleaned)
        if word.lower() not in stopwords and len(word) > 2
    ]
    return ' '.join(words)

def extract_keywords(text: str, stopwords: Set[str], min_length: int = 4) -> List[str]:
    """Extract meaningful keywords from text"""
    words = re.findall(r'\b\w+\b', text.lower())
    # Get unique words that meet criteria
    keywords = {
        word for word in words
        if (len(word) >= min_length and 
            word not in stopwords and
            not word.isdigit())
    }
    return sorted(keywords)

def sort_worksheet(ws) -> None:
    """Sort worksheet by first column (Issue number)"""
    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            # Try to convert to int for proper numeric sorting
            key = int(row[0]) if str(row[0]).isdigit() else float('inf')
        except (ValueError, TypeError):
            key = float('inf')
        data.append((key, row))
    
    # Sort by the numeric key
    data.sort(key=lambda x: x[0])
    
    # Clear and rewrite sorted data
    ws.delete_rows(2, ws.max_row)
    for _, row in data:
        ws.append(row)

if __name__ == "__main__":
    clean_data()