"""
Python interface to the Java-based DICOM tag modifier
"""
import os
import subprocess
import logging
import tempfile
from pathlib import Path
from src.utils.file_helpers import get_lib_dir

def modify_dicom_tags(input_file, dicom_tags):
    """
    Modify DICOM tags in a file using the Java DicomModifier utility.
    
    Parameters:
    - input_file: Path to the input DICOM file
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"00100020": "12345"})
    
    Returns:
    - Path to the modified DICOM file (temporary file) or None if failed
    """
    if not dicom_tags or not isinstance(dicom_tags, dict):
        logging.info("No DICOM tags to modify, returning original file")
        return input_file
    
    # Create a temporary file for the output
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"modified_{os.path.basename(input_file)}")
    
    # Get path to the Java utility
    java_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "java")
    run_script = os.path.join(java_dir, "run_dicom_modifier.bat")
    
    # Check if the utility exists
    if not os.path.exists(run_script):
        logging.error(f"DICOM Modifier utility not found at: {run_script}")
        return None
    
    # Prepare the command
    cmd = [run_script, input_file, temp_file]
    
    # Add the tag modifications
    for tag_name, tag_value in dicom_tags.items():
        if tag_value:  # Only add if the tag has a value
            cmd.append(f"{tag_name}={tag_value}")
    
    # Run the command
    logging.info(f"Modifying DICOM tags using Java utility: {' '.join(cmd)}")
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode == 0:
            logging.info(f"Successfully modified DICOM tags, output saved to: {temp_file}")
            return temp_file
        else:
            logging.error(f"Failed to modify DICOM tags: {process.stderr}")
            return None
    except Exception as e:
        logging.error(f"Error running DICOM modifier: {str(e)}")
        return None

def build_dicom_modifier():
    """
    Build the Java DICOM modifier utility
    
    Returns:
    - bool: True if successful, False otherwise
    """
    java_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "java")
    build_script = os.path.join(java_dir, "build.bat")
    
    if not os.path.exists(build_script):
        logging.error(f"Build script not found at: {build_script}")
        return False
    
    logging.info(f"Building DICOM Modifier utility using: {build_script}")
    try:
        process = subprocess.run(build_script, capture_output=True, text=True)
        
        if process.returncode == 0:
            logging.info("Successfully built DICOM Modifier utility")
            return True
        else:
            logging.error(f"Failed to build DICOM Modifier utility: {process.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error building DICOM Modifier: {str(e)}")
        return False

def cleanup_temp_files(temp_file):
    """Clean up temporary files created by the DICOM modifier"""
    if temp_file and os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            logging.info(f"Removed temporary file: {temp_file}")
        except Exception as e:
            logging.warning(f"Failed to remove temporary file: {str(e)}") 