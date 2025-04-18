#!/usr/bin/env python

"""
Test script for modifying DICOM tags and sending the modified file
"""
import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from src.dicom.dicom_modifier import modify_dicom_tags
from src.dicom.dcm4che import send_dicom_using_dcm4che, echo_dicom_using_dcm4che
from src.utils.dcm4che_validator import validate_dcm4che_setup

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def validate_setup():
    """Validate that the dcm4che environment is properly set up"""
    is_valid, report = validate_dcm4che_setup()
    print(report)
    return is_valid

def display_dicom_info(file_path):
    """Display information about the DICOM file"""
    try:
        import pydicom
        ds = pydicom.dcmread(file_path)
        print("\nDICOM File Information:")
        print("-" * 40)
        print(f"File: {file_path}")
        print(f"PatientID: {ds.PatientID if 'PatientID' in ds else 'N/A'}")
        print(f"PatientName: {ds.PatientName if 'PatientName' in ds else 'N/A'}")
        print(f"Modality: {ds.Modality if 'Modality' in ds else 'N/A'}")
        print(f"Study Description: {ds.StudyDescription if 'StudyDescription' in ds else 'N/A'}")
        print("-" * 40)
        return True
    except Exception as e:
        print(f"Error reading DICOM file: {str(e)}")
        return False

def modify_and_send(input_file, server_ip, port, ae_title, dicom_tags):
    """
    Modify DICOM tags and send the modified file to a DICOM server
    
    Args:
        input_file: Path to input DICOM file
        server_ip: DICOM server IP address
        port: DICOM server port
        ae_title: DICOM AE Title
        dicom_tags: Dict of DICOM tags to modify
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Display original file information
    print("Before modification:")
    if not display_dicom_info(input_file):
        return False
    
    # Test DICOM echo
    print(f"\nTesting DICOM echo to {server_ip}:{port} with AE Title: {ae_title}")
    echo_result = echo_dicom_using_dcm4che(server_ip, port, ae_title)
    if echo_result.returncode == 0:
        print("DICOM echo successful!")
    else:
        print(f"DICOM echo failed: {echo_result.stderr}")
        print("Continuing with modification and send anyway...")
    
    # Modify tags
    print(f"\nModifying DICOM tags...")
    modified_file = modify_dicom_tags(input_file, dicom_tags)
    
    if not modified_file:
        print("Failed to modify DICOM tags.")
        return False
    
    # Display modified file information
    print("\nAfter modification:")
    if not display_dicom_info(modified_file):
        return False
    
    # Send the modified file
    print(f"\nSending modified file to {server_ip}:{port} with AE Title: {ae_title}")
    send_result = send_dicom_using_dcm4che(modified_file, server_ip, port, ae_title)
    
    if send_result.returncode == 0:
        print("DICOM send successful!")
        print(f"Send output: {send_result.stdout}")
        return True
    else:
        print(f"DICOM send failed: {send_result.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test DICOM tag modification and sending")
    parser.add_argument("--file", required=True, help="Path to DICOM file to modify and send")
    parser.add_argument("--ip", required=True, help="DICOM server IP address")
    parser.add_argument("--port", required=True, help="DICOM server port")
    parser.add_argument("--ae-title", required=True, help="DICOM AE Title")
    parser.add_argument("--tag", action="append", help="Tag to modify in format TagNumber=Value (e.g., '00100020=ANONYMOUS')", default=[])
    
    args = parser.parse_args()
    
    setup_logging()
    
    print("Validating dcm4che setup...")
    if not validate_setup():
        print("Please resolve the issues before continuing.")
        return 1
    
    # Build tag modifications dictionary
    dicom_tags = {}
    for tag_spec in args.tag:
        parts = tag_spec.split('=', 1)
        if len(parts) == 2:
            tag, value = parts
            # Convert tag format from 0010,0020 to 00100020 if needed
            tag = tag.replace(',', '')
            dicom_tags[tag] = value
    
    # Modify and send
    success = modify_and_send(args.file, args.ip, args.port, args.ae_title, dicom_tags)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 