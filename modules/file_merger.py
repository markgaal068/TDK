import os
import openpyxl
from config import CONFIG
from utils.helpers import create_directory

def merge_excel_files():
    """
    Merge multiple Excel files into a single file
    """
    input_dir = CONFIG["merging"]["input_dir"]
    output_file = CONFIG["merging"]["output_file"]
    
    create_directory(os.path.dirname(output_file))
    
    merged_wb = openpyxl.Workbook()
    merged_ws = merged_wb.active
    merged_ws.title = "Merged Data"
    
    header_written = False
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.xlsx') and filename != os.path.basename(output_file):
            filepath = os.path.join(input_dir, filename)
            
            wb = openpyxl.load_workbook(filepath)
            ws = wb.active
            
            for row in ws.iter_rows(values_only=True):
                if not header_written:
                    merged_ws.append(row)
                    header_written = True
                elif row[0] != "Issue":  # Skip header rows
                    merged_ws.append(row)
    
    merged_wb.save(output_file)
    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    merge_excel_files()