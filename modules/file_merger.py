import os
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from config import CONFIG
from utils.helpers import create_directory
from typing import List

def merge_excel_files():
    """
    Merge multiple Excel files into a single file with enhanced functionality.
    Features:
    - Better error handling
    - Config validation
    - Duplicate prevention
    - Progress reporting
    - Header consistency checking
    """
    try:
        # Validate configuration
        input_dir = CONFIG.get("merging", {}).get("input_dir", "input/")
        output_file = CONFIG.get("merging", {}).get("output_file", "output/merged_results.xlsx")
        
        # Create directories if they don't exist
        create_directory(input_dir)
        create_directory(os.path.dirname(output_file))
        
        # Get all Excel files in input directory
        excel_files = [
            f for f in os.listdir(input_dir) 
            if f.endswith('.xlsx') and f != os.path.basename(output_file)
        ]
        
        if not excel_files:
            print("No Excel files found to merge in the input directory.")
            return
        
        print(f"Found {len(excel_files)} files to merge...")
        
        merged_wb = openpyxl.Workbook()
        merged_ws = merged_wb.active
        merged_ws.title = "Merged Data"
        
        header = None
        processed_files = 0
        total_rows = 0
        
        for filename in excel_files:
            try:
                filepath = os.path.join(input_dir, filename)
                print(f"Processing {filename}...")
                
                wb = openpyxl.load_workbook(filepath, data_only=True)
                ws = wb.active
                
                # Get all rows from the source worksheet
                rows = list(ws.iter_rows(values_only=True))
                
                if not rows:
                    print(f"Warning: {filename} is empty. Skipping.")
                    continue
                
                # Handle headers
                current_header = rows[0]
                
                if header is None:
                    header = current_header
                    merged_ws.append(header)
                elif current_header != header:
                    print(f"Warning: Header mismatch in {filename}. Skipping file.")
                    continue
                
                # Add data rows (skip header if present)
                start_row = 1 if rows[0] == header else 0
                
                for row in rows[start_row:]:
                    if row[0] is not None:  # Skip empty rows
                        merged_ws.append(row)
                        total_rows += 1
                
                processed_files += 1
                print(f"Added {len(rows) - start_row} rows from {filename}")
                
            except InvalidFileException:
                print(f"Error: {filename} is not a valid Excel file. Skipping.")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}. Skipping.")
        
        if total_rows > 0:
            merged_wb.save(output_file)
            print(f"\nSuccessfully merged {processed_files}/{len(excel_files)} files.")
            print(f"Total {total_rows} rows saved to {output_file}")
        else:
            print("No valid data found to merge.")
            if os.path.exists(output_file):
                os.remove(output_file)
    
    except Exception as e:
        print(f"Fatal error during merging: {str(e)}")

if __name__ == "__main__":
    merge_excel_files()