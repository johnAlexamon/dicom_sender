"""
File and path helper utilities for the Alexamon DICOM Sender
"""

import os
import logging
import datetime
import glob
from pathlib import Path
import pydicom

def get_logs_dir():
    """Get the path to the logs directory, regardless of where the script is run from"""
    # If we're running from the src directory
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")):
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
    # If we're running from the root directory
    elif os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")):
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    # Fallback to a relative path
    else:
        logs_dir = "logs"
    
    # Create the directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_log_filename():
    """Generate a timestamped log filename in the logs directory"""
    logs_dir = get_logs_dir()
    return os.path.join(logs_dir, f"dicom_sender_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def get_lib_dir():
    """Get the path to the lib directory, whether running from source or as a package"""
    # If we're running from the src directory
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib", "dcm4che", "lib")):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib", "dcm4che", "lib")
    # If we're running from the root directory
    elif os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", "dcm4che", "lib")):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", "dcm4che", "lib")
    # Fallback to a relative path
    else:
        return os.path.join("lib", "dcm4che", "lib")

def find_dicom_files_in_folder(folder_path):
    """
    Find all DICOM files in a folder, including files without a .dcm extension
    
    Args:
        folder_path: Path to the folder to search
        
    Returns:
        list: List of paths to DICOM files
    """
    dicom_files = []
    
    # Look for .dcm files
    dcm_files = glob.glob(os.path.join(folder_path, "**/*.dcm"), recursive=True)
    dicom_files.extend(dcm_files)
    
    # Also look for files without extension that might be DICOM
    for filename in Path(folder_path).rglob('*'):
        if filename.is_file() and not filename.suffix and str(filename) not in dicom_files:
            try:
                # Try to read as DICOM
                pydicom.dcmread(filename, stop_before_pixels=True)
                dicom_files.append(str(filename))
            except:
                # Not a DICOM file, skip
                pass
    
    return dicom_files 