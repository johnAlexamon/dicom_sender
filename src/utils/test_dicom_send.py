import os
import logging
import argparse
import time
from pathlib import Path
from src.dicom.dcm4che import send_dicom_using_dcm4che, echo_dicom_using_dcm4che
from src.utils.file_helpers import find_dicom_files_in_folder

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_echo(server_ip, server_port, server_ae_title, local_ae_title="DCMSENDER"):
    """Test DICOM echo to the server"""
    logging.info(f"Testing DICOM Echo to {server_ip}:{server_port} ({server_ae_title})...")
    start_time = time.time()
    
    success = echo_dicom_using_dcm4che(
        server_ip,
        server_port,
        server_ae_title,
        local_ae_title
    )
    
    elapsed = time.time() - start_time
    
    if success:
        logging.info(f"DICOM Echo successful! Response time: {elapsed:.2f} seconds")
        return True
    else:
        logging.error(f"DICOM Echo failed after {elapsed:.2f} seconds")
        return False

def test_send_file(file_path, server_ip, server_port, server_ae_title, local_ae_title="DCMSENDER"):
    """Test sending a single DICOM file"""
    if not os.path.exists(file_path):
        logging.error(f"DICOM file not found: {file_path}")
        return False
    
    logging.info(f"Sending DICOM file: {file_path}")
    logging.info(f"  To server: {server_ip}:{server_port} ({server_ae_title})")
    
    start_time = time.time()
    
    success = send_dicom_using_dcm4che(
        file_path,
        server_ip,
        server_port,
        server_ae_title,
        local_ae_title
    )
    
    elapsed = time.time() - start_time
    
    if success:
        logging.info(f"DICOM file sent successfully! Time: {elapsed:.2f} seconds")
        return True
    else:
        logging.error(f"Failed to send DICOM file after {elapsed:.2f} seconds")
        return False

def test_send_folder(folder_path, server_ip, server_port, server_ae_title, local_ae_title="DCMSENDER"):
    """Test sending all DICOM files in a folder"""
    if not os.path.exists(folder_path):
        logging.error(f"Folder not found: {folder_path}")
        return False
    
    dicom_files = find_dicom_files_in_folder(folder_path)
    
    if not dicom_files:
        logging.error(f"No DICOM files found in folder: {folder_path}")
        return False
    
    logging.info(f"Found {len(dicom_files)} DICOM files in folder: {folder_path}")
    
    success_count = 0
    failure_count = 0
    
    for idx, file_path in enumerate(dicom_files, 1):
        logging.info(f"Processing file {idx}/{len(dicom_files)}: {file_path}")
        
        if test_send_file(file_path, server_ip, server_port, server_ae_title, local_ae_title):
            success_count += 1
        else:
            failure_count += 1
    
    logging.info(f"Completed sending {len(dicom_files)} DICOM files")
    logging.info(f"Success: {success_count}, Failures: {failure_count}")
    
    return failure_count == 0

def main():
    """Main function to run the DICOM send test"""
    parser = argparse.ArgumentParser(description="Test DICOM sending using dcm4che")
    
    parser.add_argument("--server", required=True, help="DICOM server IP address")
    parser.add_argument("--port", type=int, required=True, help="DICOM server port")
    parser.add_argument("--aet", required=True, help="Server AE Title")
    parser.add_argument("--local-aet", default="DCMSENDER", help="Local AE Title (default: DCMSENDER)")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--echo", action="store_true", help="Just test DICOM echo")
    group.add_argument("--file", help="Path to a single DICOM file to send")
    group.add_argument("--folder", help="Path to a folder containing DICOM files")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.echo:
        success = test_echo(args.server, args.port, args.aet, args.local_aet)
    elif args.file:
        success = test_send_file(args.file, args.server, args.port, args.aet, args.local_aet)
    elif args.folder:
        success = test_send_folder(args.folder, args.server, args.port, args.aet, args.local_aet)
    else:
        logging.error("No action specified (echo, file, or folder)")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 