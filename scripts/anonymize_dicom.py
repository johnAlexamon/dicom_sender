#!/usr/bin/env python

"""
Script for anonymizing DICOM files for testing purposes
"""
import os
import sys
import logging
import argparse
import random
import string
import datetime
from pathlib import Path
import uuid

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from src.dicom.dicom_modifier import modify_dicom_tags, build_dicom_modifier, cleanup_temp_files
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

def generate_random_id(length=8):
    """Generate a random ID with specified length"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_random_name():
    """Generate a random patient name in DICOM format (LAST^FIRST)"""
    last_names = ["SMITH", "JONES", "WILLIAMS", "BROWN", "TAYLOR", "ANONYMOUS", "TEST", "DOE"]
    first_names = ["JOHN", "JANE", "MICHAEL", "ROBERT", "SARAH", "MARY", "JAMES", "TEST"]
    
    last = random.choice(last_names)
    first = random.choice(first_names)
    return f"{last}^{first}"

def generate_random_date():
    """Generate a random date in YYYYMMDD format within the past 5 years"""
    today = datetime.date.today()
    random_days = random.randint(0, 365 * 5)  # Up to 5 years in the past
    random_date = today - datetime.timedelta(days=random_days)
    return random_date.strftime("%Y%m%d")

def anonymize_dicom(input_file, output_file=None, randomize=False):
    """
    Anonymize a DICOM file
    
    Args:
        input_file: Path to input DICOM file
        output_file: Path to output file (if None, will be generated)
        randomize: If True, use random values, otherwise use fixed "ANONYMOUS" values
        
    Returns:
        str: Path to the anonymized file or None if failed
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return None
    
    if output_file is None:
        # Generate output filename in the same directory
        dir_path = os.path.dirname(input_file)
        filename = os.path.basename(input_file)
        base_name, ext = os.path.splitext(filename)
        output_file = os.path.join(dir_path, f"{base_name}_anonymized{ext}")
    
    # Define anonymization tags
    dicom_tags = {}
    
    if randomize:
        # Use random values
        dicom_tags["00100010"] = generate_random_name()
        dicom_tags["00100020"] = generate_random_id()
        dicom_tags["00100030"] = generate_random_date()
        dicom_tags["00100040"] = random.choice(["M", "F", "O"])
        dicom_tags["00081030"] = f"ANONYMOUS STUDY {generate_random_id(4)}"
        # Generate a new SOP Instance UID
        dicom_tags["00080018"] = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 10000000}"
    else:
        # Use fixed values
        dicom_tags["00100010"] = "ANONYMOUS^PATIENT"
        dicom_tags["00100020"] = "ANONYMOUS"
        dicom_tags["00100030"] = ""  # Remove birth date
        dicom_tags["00100040"] = "O"  # Other
        dicom_tags["00081030"] = "ANONYMOUS STUDY"
    
    # Additional tags to remove/anonymize
    dicom_tags["00081070"] = ""  # Operator's Name
    dicom_tags["00081090"] = ""  # Manufacturer's Model Name
    dicom_tags["00080090"] = "ANONYMOUS^DOCTOR"  # Referring Physician
    
    print(f"Anonymizing DICOM file: {input_file}")
    print(f"Output file: {output_file}")
    print("Tags to modify:")
    for tag, value in dicom_tags.items():
        print(f"  {tag}: {value}")
    
    # Create a temporary modified file
    temp_file = modify_dicom_tags(input_file, dicom_tags)
    
    if not temp_file:
        print("Failed to modify DICOM tags.")
        return None
    
    # Move the temporary file to the desired output location
    try:
        import shutil
        shutil.copy2(temp_file, output_file)
        cleanup_temp_files(temp_file)
        print(f"Anonymized file saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error copying temporary file: {str(e)}")
        return temp_file
    
def anonymize_folder(input_folder, output_folder=None, randomize=False):
    """
    Anonymize all DICOM files in a folder
    
    Args:
        input_folder: Path to input folder
        output_folder: Path to output folder (if None, will add "_anonymized" to the input folder name)
        randomize: If True, use random values, otherwise use fixed "ANONYMOUS" values
        
    Returns:
        int: Number of files successfully anonymized
    """
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' not found or not a directory.")
        return 0
    
    if output_folder is None:
        # Generate output folder name
        parent_dir = os.path.dirname(input_folder)
        folder_name = os.path.basename(input_folder)
        output_folder = os.path.join(parent_dir, f"{folder_name}_anonymized")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Anonymizing all DICOM files in: {input_folder}")
    print(f"Output folder: {output_folder}")
    
    # Find all DICOM files
    from src.utils.file_helpers import find_dicom_files_in_folder
    dicom_files = find_dicom_files_in_folder(input_folder)
    
    if not dicom_files:
        print("No DICOM files found in the folder.")
        return 0
    
    print(f"Found {len(dicom_files)} DICOM files.")
    
    # Anonymize each file
    success_count = 0
    for i, file_path in enumerate(dicom_files, 1):
        try:
            # Generate output path
            rel_path = os.path.relpath(file_path, input_folder)
            output_path = os.path.join(output_folder, rel_path)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            print(f"[{i}/{len(dicom_files)}] Processing: {rel_path}")
            
            # Anonymize the file
            anonymized_file = anonymize_dicom(file_path, output_path, randomize)
            
            if anonymized_file:
                success_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Anonymization complete. {success_count}/{len(dicom_files)} files processed successfully.")
    return success_count

def main():
    parser = argparse.ArgumentParser(description="Anonymize DICOM files for testing purposes")
    
    # Create mutually exclusive group for file or folder
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", help="Path to DICOM file to anonymize")
    input_group.add_argument("--folder", help="Path to folder containing DICOM files to anonymize")
    
    parser.add_argument("--output", help="Path to output file or folder (optional)")
    parser.add_argument("--randomize", action="store_true", help="Use random values instead of fixed 'ANONYMOUS' values")
    
    args = parser.parse_args()
    
    setup_logging()
    
    print("Validating dcm4che setup...")
    if not validate_setup():
        print("Please resolve the issues before continuing.")
        return 1
    
    # Ensure the DicomModifier is built
    if not build_dicom_modifier():
        print("Failed to build the DicomModifier utility.")
        return 1
    
    if args.file:
        # Anonymize a single file
        success = anonymize_dicom(args.file, args.output, args.randomize)
        return 0 if success else 1
    elif args.folder:
        # Anonymize all files in a folder
        success_count = anonymize_folder(args.folder, args.output, args.randomize)
        return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 