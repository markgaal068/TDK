import os
import openpyxl
from collections import Counter
from config import CONFIG
from utils.helpers import create_directory

def analyze_keywords():
    """
    Analyze and extract most frequent keywords
    """
    input_file = CONFIG["cleaning"]["output_file"]
    output_file = CONFIG["analysis"]["output_file"]
    top_n = CONFIG["analysis"]["top_n"]
    
    create_directory(os.path.dirname(output_file))
    
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active
    
    keywords = []
    for row in range(2, ws.max_row + 1):
        keywords_cell = ws.cell(row=row, column=5).value
        if keywords_cell:
            keywords.extend([kw.strip() for kw in keywords_cell.split(',') if kw.strip()])
    
    keyword_counts = Counter(keywords)
    top_keywords = keyword_counts.most_common(top_n)
    
    analysis_wb = openpyxl.Workbook()
    analysis_ws = analysis_wb.active
    analysis_ws.title = "Keyword Analysis"
    analysis_ws.append(["Keyword", "Frequency"])
    
    for keyword, count in top_keywords:
        analysis_ws.append([keyword, count])
    
    analysis_wb.save(output_file)
    print(f"Keyword analysis saved to {output_file}")