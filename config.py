# config.py
import os

def get_project_root():
    """Get the project root directory"""
    return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    """Get the absolute path for the database file"""
    root_dir = get_project_root()
    data_dir = os.path.join(root_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'crypto_transactions.db')