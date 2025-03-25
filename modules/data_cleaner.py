import openpyxl
import re
from config import CONFIG
from utils.helpers import create_directory
import os

def clean_data():
    """
    Clean the extracted data by removing stopwords and sorting
    """
    input_file = CONFIG["merging"]["output_file"]
    output_file = CONFIG["cleaning"]["output_file"]
    stopwords = CONFIG["cleaning"]["stopwords"]
    
    create_directory(os.path.dirname(output_file))
    
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active
    
    # Add new columns for cleaned data
    ws.cell(row=1, column=4, value="Cleaned Content")
    ws.cell(row=1, column=5, value="Keywords")
    
    for row in range(2, ws.max_row + 1):
        content = ws.cell(row=row, column=2).value
        if content:
            # Remove stopwords
            cleaned_content = ' '.join([
                word for word in re.findall(r'\b\w+\b', content.lower()) 
                if word not in stopwords
            ])
            
            # Extract potential keywords (longer words)
            keywords = ', '.join({
                word for word in re.findall(r'\b\w{4,}\b', cleaned_content)
                if word not in stopwords
            })
            
            ws.cell(row=row, column=4, value=cleaned_content)
            ws.cell(row=row, column=5, value=keywords)
    
    # Sort by issue number
    data = list(ws.iter_rows(min_row=2, values_only=True))
    data.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0)
    
    # Clear and rewrite sorted data
    ws.delete_rows(2, ws.max_row)
    for row in data:
        ws.append(row)
    
    wb.save(output_file)
    print(f"Cleaned data saved to {output_file}")

if __name__ == "__main__":
    clean_data()