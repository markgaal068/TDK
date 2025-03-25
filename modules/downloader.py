import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import CONFIG
from utils.helpers import create_directory

def download_journal_issues():
    """
    Download all journal issues from the specified website
    """
    base_url = CONFIG["download"]["base_url"]
    output_dir = CONFIG["download"]["output_dir"]
    start_issue = CONFIG["download"]["start_issue"]
    end_issue = CONFIG["download"]["end_issue"]
    
    create_directory(output_dir)
    
    for issue_num in range(start_issue, end_issue + 1):
        try:
            issue_url = urljoin(base_url, f"issue-{issue_num}")
            response = requests.get(issue_url, timeout=10)
            response.raise_for_status()
            
            filename = os.path.join(output_dir, f"issue_{issue_num}.html")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Successfully downloaded issue {issue_num}")
            
        except Exception as e:
            print(f"Failed to download issue {issue_num}: {str(e)}")
    
    print("Download process completed.")

if __name__ == "__main__":
    download_journal_issues()