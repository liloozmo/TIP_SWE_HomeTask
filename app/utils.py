from datetime import datetime
import os

def get_current_time() ->str:
    # Includes milliseconds to prevent filename collision
    return datetime.now().strftime("%d%m%Y_%H%M%S_%f")

def ensure_output_directory(directory:str):
    os.makedirs(directory,exist_ok=True)