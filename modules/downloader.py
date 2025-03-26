import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import CONFIG
from utils.helpers import create_directory
from typing import List, Dict
import time
from tqdm import tqdm

def download_journal_issues(base_url: str = None, start_issue: int = None, end_issue: int = None) -> List[str]:
    """
    Download all journal issues from the specified website
    
    Args:
        base_url (str, optional): Base URL for the journal. If None, uses config value.
        start_issue (int, optional): Starting issue number. If None, uses config value.
        end_issue (int, optional): Ending issue number. If None, uses config value.
    
    Returns:
        List[str]: List of successfully downloaded file paths
    """
    # Use provided values or fall back to config
    base_url = base_url or CONFIG["download"]["base_url"]
    output_dir = CONFIG["download"]["output_dir"]
    start_issue = start_issue or CONFIG["download"].get("start_issue", 1)
    end_issue = end_issue or CONFIG["download"].get("end_issue", 1)
    max_retries = CONFIG["download"].get("max_retries", 3)
    timeout = CONFIG["download"].get("timeout", 30)
    
    create_directory(output_dir)
    downloaded_files = []
    
    # Create progress bar
    pbar = tqdm(range(start_issue, end_issue + 1), desc="Downloading issues")
    
    for issue_num in pbar:
        retry_count = 0
        while retry_count < max_retries:
            try:
                issue_url = urljoin(base_url, f"issue-{issue_num}")
                pbar.set_description(f"Downloading issue {issue_num}")
                
                response = requests.get(issue_url, timeout=timeout)
                response.raise_for_status()
                
                # Parse HTML to find PDF links
                soup = BeautifulSoup(response.text, 'html.parser')
                pdf_links = soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))
                
                if not pdf_links:
                    print(f"\nNo PDF links found in issue {issue_num}")
                    break
                
                # Download each PDF
                for link in pdf_links:
                    pdf_url = urljoin(issue_url, link['href'])
                    pdf_filename = os.path.join(output_dir, f"issue_{issue_num}_{os.path.basename(pdf_url)}")
                    
                    pdf_response = requests.get(pdf_url, timeout=timeout)
                    pdf_response.raise_for_status()
                    
                    with open(pdf_filename, 'wb') as f:
                        f.write(pdf_response.content)
                    
                    downloaded_files.append(pdf_filename)
                    print(f"\nSuccessfully downloaded: {pdf_filename}")
                
                # Add delay between requests to be nice to the server
                time.sleep(1)
                break
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count == max_retries:
                    print(f"\nFailed to download issue {issue_num} after {max_retries} attempts: {str(e)}")
                else:
                    print(f"\nRetrying issue {issue_num} ({retry_count}/{max_retries})")
                    time.sleep(2 ** retry_count)  # Exponential backoff
    
    print(f"\nDownload process completed. Successfully downloaded {len(downloaded_files)} files.")
    return downloaded_files

if __name__ == "__main__":
    try:
        downloaded_files = download_journal_issues()
        print(f"Files downloaded to: {CONFIG['download']['output_dir']}")
    except Exception as e:
        print(f"Fatal error: {str(e)}")