import os
import re
import pandas as pd
from PyPDF2 import PdfReader


def extract_content_from_pdf(pdf_path, start_marker="Abstract", end_marker="Key Words"):
    try:
        reader = PdfReader(pdf_path)
        full_text = ""

        # Concatenate text from all pages
        for page in reader.pages:
            full_text += page.extract_text()

        # Find content between start_marker and end_marker
        match = re.search(f"{start_marker}(.*?){end_marker}", full_text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        else:
            return None
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None


def process_pdfs_in_folder(folder_path, output_excel="output.xlsx"):
    data = []
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    szaml = 0
    for pdf_file in pdf_files:
        szaml+=1
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"{szaml}. → Processing {pdf_file}...")
        content = extract_content_from_pdf(pdf_path)

        if content:
            data.append({"Filename": pdf_file, "Abstract_Content": content})
        else:
            print(f"No content found in {pdf_file}.")

    # Save data to Excel
    if data:
        df = pd.DataFrame(data)
        df.to_excel(output_excel, index=False)
        print(f"Data saved to {output_excel}")
    else:
        print("No valid content found in any PDF.")


# Define the folder containing PDFs and the output Excel file
pdf_folder = "D:/GTG"  # Replace with the folder containing your PDFs
output_file = "output.xlsx"

# Run the processing function
process_pdfs_in_folder(pdf_folder, output_file)