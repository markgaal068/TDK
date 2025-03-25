import os

def create_directory(directory_path):
    """
    Create directory if it doesn't exist
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")