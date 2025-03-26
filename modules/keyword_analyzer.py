import os
import openpyxl
from collections import Counter
from config import CONFIG
from utils.helpers import create_directory
from typing import List, Tuple, Dict
import logging

def setup_logging():
    """Configure logging for the analysis process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('keyword_analysis.log'),
            logging.StreamHandler()
        ]
    )

def analyze_keywords():
    """
    Enhanced keyword analysis with:
    - Better error handling
    - Config validation
    - Progress tracking
    - Advanced keyword processing
    - Multiple output formats
    """
    try:
        setup_logging()
        logging.info("Starting keyword analysis process")

        # Validate and get configuration with defaults
        config_analysis = CONFIG.get("analysis", {})
        config_cleaning = CONFIG.get("cleaning", {})
        
        input_file = config_cleaning.get("output_file", "output/cleaned_data.xlsx")
        output_file = config_analysis.get("output_file", "output/keyword_analysis.xlsx")
        top_n = config_analysis.get("top_n", 50)
        min_keyword_length = config_analysis.get("min_keyword_length", 3)
        exclude_numbers = config_analysis.get("exclude_numbers", True)
        
        # Create output directory if needed
        create_directory(os.path.dirname(output_file))
        logging.info(f"Output will be saved to: {output_file}")

        # Load workbook with error handling
        try:
            logging.info(f"Loading input file: {input_file}")
            wb = openpyxl.load_workbook(input_file)
            ws = wb.active
        except FileNotFoundError:
            raise Exception(f"Input file not found: {input_file}")
        except Exception as e:
            raise Exception(f"Error loading workbook: {str(e)}")

        # Validate worksheet
        if ws.max_row < 2:
            logging.warning("No data found to analyze (empty worksheet)")
            return

        # Extract and process keywords
        logging.info("Extracting keywords from worksheet...")
        all_keywords = extract_all_keywords(ws, min_keyword_length, exclude_numbers)
        
        if not all_keywords:
            logging.warning("No keywords found in the dataset")
            return

        # Analyze keyword frequencies
        logging.info("Analyzing keyword frequencies...")
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(top_n)
        
        # Generate analysis report
        logging.info("Generating analysis report...")
        generate_analysis_report(output_file, top_keywords)
        
        # Additional analysis (optional)
        if config_analysis.get("generate_wordcloud", False):
            generate_wordcloud(keyword_counts, output_file)
        
        logging.info(f"Successfully completed analysis. Top {top_n} keywords saved to {output_file}")

    except Exception as e:
        logging.error(f"Error in keyword analysis: {str(e)}", exc_info=True)

def extract_all_keywords(worksheet, min_length: int = 3, exclude_numbers: bool = True) -> List[str]:
    """
    Extract and preprocess keywords from worksheet
    """
    keywords = []
    total_rows = worksheet.max_row - 1
    processed_rows = 0
    
    for row in range(2, worksheet.max_row + 1):
        try:
            keywords_cell = worksheet.cell(row=row, column=5).value
            if keywords_cell:
                # Process keywords with additional filtering
                row_keywords = [
                    kw.strip().lower() 
                    for kw in keywords_cell.split(',') 
                    if (kw.strip() and 
                        len(kw.strip()) >= min_length and
                        (not exclude_numbers or not kw.strip().isdigit()))
                ]
                keywords.extend(row_keywords)
            
            processed_rows += 1
            if processed_rows % 100 == 0:
                logging.info(f"Processed {processed_rows}/{total_rows} rows...")
                
        except Exception as e:
            logging.warning(f"Error processing row {row}: {str(e)}")
            continue
    
    return keywords

def generate_analysis_report(output_path: str, keyword_data: List[Tuple[str, int]]):
    """
    Generate Excel report with keyword analysis
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Keyword Analysis"
    
    # Header with additional metadata
    ws.append(["Keyword", "Frequency", "Percentage"])
    
    total_occurrences = sum(count for _, count in keyword_data)
    
    for keyword, count in keyword_data:
        percentage = (count / total_occurrences) * 100
        ws.append([keyword, count, f"{percentage:.2f}%"])
    
    # Add summary statistics
    ws.append([])
    ws.append(["Summary Statistics", ""])
    ws.append(["Total unique keywords", len(keyword_data)])
    ws.append(["Total occurrences", total_occurrences])
    
    # Formatting
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    
    wb.save(output_path)

def generate_wordcloud(keyword_counts: Dict[str, int], output_path: str):
    """
    Optional: Generate wordcloud visualization
    """
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        
        logging.info("Generating wordcloud...")
        
        wordcloud = WordCloud(
            width=800,
            height=600,
            background_color='white'
        ).generate_from_frequencies(keyword_counts)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Save wordcloud image
        img_path = os.path.splitext(output_path)[0] + '_wordcloud.png'
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Wordcloud saved to: {img_path}")
    except ImportError:
        logging.warning("WordCloud package not available. Skipping wordcloud generation.")
    except Exception as e:
        logging.warning(f"Error generating wordcloud: {str(e)}")

if __name__ == "__main__":
    analyze_keywords()