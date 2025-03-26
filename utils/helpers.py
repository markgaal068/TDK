import os
import shutil
from typing import List, Optional
import logging
from pathlib import Path

def create_directory(directory_path: str) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        directory_path (str): Path to the directory to create
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logging.info(f"Created directory: {directory_path}")
    except Exception as e:
        logging.error(f"Failed to create directory {directory_path}: {str(e)}")
        raise

def clean_directory(directory_path: str, pattern: str = "*") -> None:
    """
    Clean all files in a directory matching the pattern
    
    Args:
        directory_path (str): Path to the directory to clean
        pattern (str): File pattern to match (default: "*")
    """
    try:
        if os.path.exists(directory_path):
            for file in Path(directory_path).glob(pattern):
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
            logging.info(f"Cleaned directory: {directory_path}")
    except Exception as e:
        logging.error(f"Failed to clean directory {directory_path}: {str(e)}")
        raise

def get_file_list(directory_path: str, pattern: str = "*") -> List[str]:
    """
    Get list of files in directory matching the pattern
    
    Args:
        directory_path (str): Path to the directory to search
        pattern (str): File pattern to match (default: "*")
    
    Returns:
        List[str]: List of file paths
    """
    try:
        if not os.path.exists(directory_path):
            return []
        
        return [str(f) for f in Path(directory_path).glob(pattern) if f.is_file()]
    except Exception as e:
        logging.error(f"Failed to get file list from {directory_path}: {str(e)}")
        return []

def safe_remove_file(file_path: str) -> bool:
    """
    Safely remove a file if it exists
    
    Args:
        file_path (str): Path to the file to remove
    
    Returns:
        bool: True if file was removed or didn't exist, False if removal failed
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Removed file: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to remove file {file_path}: {str(e)}")
        return False

def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        Optional[int]: File size in bytes or None if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None
    except Exception as e:
        logging.error(f"Failed to get file size for {file_path}: {str(e)}")
        return None

def ensure_file_extension(file_path: str, extension: str) -> str:
    """
    Ensure file has the specified extension
    
    Args:
        file_path (str): Path to the file
        extension (str): Desired extension (with or without dot)
    
    Returns:
        str: File path with correct extension
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    if not file_path.lower().endswith(extension.lower()):
        return file_path + extension
    return file_path