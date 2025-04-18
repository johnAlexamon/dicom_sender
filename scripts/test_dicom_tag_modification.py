"""
Test script for the DICOM tag modification feature using Java DicomModifier
"""
import os
import sys
import logging
import argparse
import pydicom

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from src.dicom.dicom_modifier import modify_dicom_tags, build_dicom_modifier
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

def display_dicom_tags(file_path):
    """Display key DICOM tags from a file"""
    try:
        ds = pydicom.dcmread(file_path)
        print("\nDICOM Tags:")
        print("-" * 40)
        
        # Display common tags
        tags_to_show = [
            ('PatientID', '0010,0020'),
            ('PatientName', '0010,0010'),
            ('StudyDescription', '0008,1030'),
            ('SeriesDescription', '0008,103E'),
            ('Modality', '0008,0060'),
            ('SOPInstanceUID', '0008,0018')
        ]
        
        for name, tag in tags_to_show:
            try:
                tag_obj = pydicom.tag.Tag(tag.replace(',', ''))
                if tag_obj in ds:
                    print(f"{name} ({tag}): {ds[tag_obj].value}")
            except:
                pass
        
        print("-" * 40)
        return True
    except Exception as e:
        print(f"Error reading DICOM file: {str(e)}")
        return False

def test_tag_modification(input_file, tags_to_modify):
    """Test modifying DICOM tags and display the before/after comparison"""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    print(f"\nModifying DICOM file: {input_file}")
    print("Before modification:")
    display_dicom_tags(input_file)
    
    # Build tag modifications dictionary
    dicom_tags = {}
    for tag_spec in tags_to_modify:
        parts = tag_spec.split('=', 1)
        if len(parts) == 2:
            tag, value = parts
            # Convert tag format from 0010,0020 to 00100020 if needed
            tag = tag.replace(',', '')
            dicom_tags[tag] = value
    
    # Modify tags
    modified_file = modify_dicom_tags(input_file, dicom_tags)
    
    if modified_file:
        print("\nAfter modification:")
        display_dicom_tags(modified_file)
        
        print(f"\nModified file saved as: {modified_file}")
        print("\nModification successful!")
        return True
    else:
        print("\nFailed to modify DICOM tags.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test DICOM tag modification")
    parser.add_argument("--file", required=True, help="Path to DICOM file to modify")
    parser.add_argument("--tag", action="append", help="Tag to modify in format TagNumber=Value (e.g., '00100020=ANONYMOUS' or '0010,0020=ANONYMOUS')", default=[])
    
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
    
    # Test tag modification
    success = test_tag_modification(args.file, args.tag)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 