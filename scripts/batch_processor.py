#!/usr/bin/env python

"""
Batch processor for DICOM files - can anonymize, modify tags, and/or send multiple files
"""
import os
import sys
import logging
import argparse
import threading
import time
import concurrent.futures
from pathlib import Path
import queue

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from src.dicom.dicom_modifier import modify_dicom_tags, build_dicom_modifier, cleanup_temp_files
from src.dicom.dcm4che import send_dicom_using_dcm4che, echo_dicom_using_dcm4che
from src.utils.dcm4che_validator import validate_dcm4che_setup
from src.utils.file_helpers import find_dicom_files_in_folder

class BatchProcessor:
    """Batch processor for DICOM operations"""
    
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.file_queue = queue.Queue()
        self.results = []
        self.success_count = 0
        self.error_count = 0
        self.stop_event = threading.Event()
        self.workers = []
        self.progress_lock = threading.Lock()

    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def validate_setup(self):
        """Validate that the dcm4che environment is properly set up"""
        is_valid, report = validate_dcm4che_setup()
        print(report)
        return is_valid

    def add_files_from_folder(self, folder_path):
        """Add all DICOM files from a folder to the processing queue"""
        files = find_dicom_files_in_folder(folder_path)
        if not files:
            print(f"No DICOM files found in folder: {folder_path}")
            return 0
            
        for file in files:
            self.file_queue.put(file)
            
        print(f"Added {len(files)} DICOM files to the processing queue")
        return len(files)
        
    def add_file(self, file_path):
        """Add a single file to the processing queue"""
        if os.path.exists(file_path):
            self.file_queue.put(file_path)
            return 1
        else:
            print(f"File not found: {file_path}")
            return 0
            
    def worker_thread(self, worker_id, operation, **kwargs):
        """Worker thread for processing DICOM files"""
        while not self.stop_event.is_set():
            try:
                # Get a file from the queue with a timeout
                file_path = self.file_queue.get(timeout=0.5)
                
                # Process the file
                with self.progress_lock:
                    total = self.success_count + self.error_count + self.file_queue.qsize()
                    print(f"Worker {worker_id}: Processing file {self.success_count + self.error_count + 1}/{total}: {os.path.basename(file_path)}")
                
                result = operation(file_path, **kwargs)
                
                # Track the result
                with self.progress_lock:
                    if result['success']:
                        self.success_count += 1
                    else:
                        self.error_count += 1
                    self.results.append(result)
                
                # Mark the task as done
                self.file_queue.task_done()
                
            except queue.Empty:
                # No more files in the queue
                break
            except Exception as e:
                # Handle any other exceptions
                with self.progress_lock:
                    print(f"Worker {worker_id} error: {str(e)}")
                    self.error_count += 1
                    self.results.append({
                        'file': file_path if 'file_path' in locals() else 'unknown',
                        'success': False,
                        'error': str(e)
                    })
                # Mark the task as done if we got a file
                if 'file_path' in locals():
                    self.file_queue.task_done()
    
    def process_batch(self, operation, **kwargs):
        """
        Process all files in the queue using the specified operation
        
        Args:
            operation: Function to call for each file
            **kwargs: Additional arguments to pass to the operation
            
        Returns:
            dict: Results summary
        """
        # Start worker threads
        self.workers = []
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self.worker_thread,
                args=(i+1, operation),
                kwargs=kwargs
            )
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
        # Start a progress reporting thread
        def report_progress():
            last_count = 0
            while not self.stop_event.is_set() and any(w.is_alive() for w in self.workers):
                with self.progress_lock:
                    total = self.success_count + self.error_count + self.file_queue.qsize()
                    current = self.success_count + self.error_count
                    if current != last_count:
                        print(f"Progress: {current}/{total} files processed ({self.success_count} success, {self.error_count} errors)")
                        last_count = current
                time.sleep(2)
                
        progress_thread = threading.Thread(target=report_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Wait for all files to be processed
        for worker in self.workers:
            worker.join()
            
        # Set the stop event to terminate the progress thread
        self.stop_event.set()
        progress_thread.join()
        
        # Final progress report
        print(f"Completed processing {self.success_count + self.error_count} files")
        print(f"Success: {self.success_count}, Errors: {self.error_count}")
        
        return {
            'total': self.success_count + self.error_count,
            'success': self.success_count,
            'errors': self.error_count,
            'results': self.results
        }

    # Operations that can be performed on DICOM files
    
    def anonymize_operation(self, file_path, output_dir=None, randomize=False):
        """
        Anonymize a DICOM file
        
        Args:
            file_path: Path to the DICOM file
            output_dir: Directory to save the anonymized file (optional)
            randomize: Whether to use random values (True) or fixed "ANONYMOUS" values (False)
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Import here to avoid circular import
            from scripts.anonymize_dicom import anonymize_dicom, generate_random_id, generate_random_name, generate_random_date
            import uuid
            import random
            
            # Prepare output path
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.basename(file_path)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_anonymized.dcm")
            else:
                dir_path = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                output_path = os.path.join(dir_path, f"{os.path.splitext(filename)[0]}_anonymized.dcm")
            
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
            
            # Modify tags
            temp_file = modify_dicom_tags(file_path, dicom_tags)
            
            if not temp_file:
                return {
                    'file': file_path,
                    'success': False,
                    'error': "Failed to modify DICOM tags"
                }
            
            # Move the temporary file to the output location
            import shutil
            shutil.copy2(temp_file, output_path)
            cleanup_temp_files(temp_file)
            
            return {
                'file': file_path,
                'output': output_path,
                'success': True
            }
            
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'error': str(e)
            }
            
    def send_operation(self, file_path, server_ip, port, ae_title):
        """
        Send a DICOM file to a server
        
        Args:
            file_path: Path to the DICOM file
            server_ip: DICOM server IP address
            port: DICOM server port
            ae_title: DICOM AE Title
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Send the file
            result = send_dicom_using_dcm4che(file_path, server_ip, port, ae_title)
            
            if result.returncode == 0:
                return {
                    'file': file_path,
                    'success': True,
                    'output': result.stdout
                }
            else:
                return {
                    'file': file_path,
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'error': str(e)
            }
            
    def modify_and_send_operation(self, file_path, server_ip, port, ae_title, dicom_tags):
        """
        Modify DICOM tags and send the file to a server
        
        Args:
            file_path: Path to the DICOM file
            server_ip: DICOM server IP address
            port: DICOM server port
            ae_title: DICOM AE Title
            dicom_tags: Dictionary of DICOM tags to modify
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Modify tags
            temp_file = modify_dicom_tags(file_path, dicom_tags)
            
            if not temp_file:
                return {
                    'file': file_path,
                    'success': False,
                    'error': "Failed to modify DICOM tags"
                }
            
            # Send the modified file
            result = send_dicom_using_dcm4che(temp_file, server_ip, port, ae_title)
            
            # Clean up the temporary file
            cleanup_temp_files(temp_file)
            
            if result.returncode == 0:
                return {
                    'file': file_path,
                    'success': True,
                    'output': result.stdout
                }
            else:
                return {
                    'file': file_path,
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'error': str(e)
            }

def main():
    parser = argparse.ArgumentParser(description="Batch process DICOM files")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--folder", help="Process all DICOM files in the specified folder")
    input_group.add_argument("--file", help="Process a single DICOM file")
    
    # Operation options
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument("--anonymize", action="store_true", help="Anonymize DICOM files")
    operation_group.add_argument("--send", action="store_true", help="Send DICOM files to a server")
    operation_group.add_argument("--modify-and-send", action="store_true", help="Modify tags and send DICOM files")
    
    # Server arguments (required for send and modify-and-send)
    server_group = parser.add_argument_group("Server options (required for --send and --modify-and-send)")
    server_group.add_argument("--ip", help="DICOM server IP address")
    server_group.add_argument("--port", help="DICOM server port")
    server_group.add_argument("--ae-title", help="DICOM AE Title")
    
    # Anonymization options
    anonymize_group = parser.add_argument_group("Anonymization options")
    anonymize_group.add_argument("--output-dir", help="Directory to save anonymized files")
    anonymize_group.add_argument("--randomize", action="store_true", help="Use random values instead of fixed 'ANONYMOUS' values")
    
    # Tag modification options
    modify_group = parser.add_argument_group("Tag modification options")
    modify_group.add_argument("--tag", action="append", help="Tag to modify in format TagNumber=Value (e.g., '00100020=ANONYMOUS')", default=[])
    
    # Other options
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads (default: 4)")
    
    args = parser.parse_args()
    
    # Create and configure the batch processor
    processor = BatchProcessor(num_workers=args.workers)
    processor.setup_logging()
    
    print("Validating dcm4che setup...")
    if not processor.validate_setup():
        print("Please resolve the issues before continuing.")
        return 1
    
    # Ensure the DicomModifier is built if needed
    if args.anonymize or args.modify_and_send or args.tag:
        if not build_dicom_modifier():
            print("Failed to build the DicomModifier utility.")
            return 1
    
    # Add files to the processing queue
    if args.folder:
        count = processor.add_files_from_folder(args.folder)
        if count == 0:
            return 1
    elif args.file:
        count = processor.add_file(args.file)
        if count == 0:
            return 1
    
    # Build tag modifications dictionary if needed
    dicom_tags = {}
    if args.tag:
        for tag_spec in args.tag:
            parts = tag_spec.split('=', 1)
            if len(parts) == 2:
                tag, value = parts
                # Convert tag format from 0010,0020 to 00100020 if needed
                tag = tag.replace(',', '')
                dicom_tags[tag] = value
    
    # Process the batch based on the selected operation
    if args.anonymize:
        print("Starting batch anonymization...")
        results = processor.process_batch(
            processor.anonymize_operation,
            output_dir=args.output_dir,
            randomize=args.randomize
        )
    elif args.send:
        # Validate server parameters
        if not args.ip or not args.port or not args.ae_title:
            print("Error: --ip, --port, and --ae-title are required for sending DICOM files")
            return 1
            
        print(f"Starting batch sending to {args.ip}:{args.port}...")
        results = processor.process_batch(
            processor.send_operation,
            server_ip=args.ip,
            port=args.port,
            ae_title=args.ae_title
        )
    elif args.modify_and_send:
        # Validate server parameters
        if not args.ip or not args.port or not args.ae_title:
            print("Error: --ip, --port, and --ae-title are required for sending DICOM files")
            return 1
            
        if not args.tag:
            print("Error: At least one --tag is required for modify-and-send operation")
            return 1
            
        print(f"Starting batch tag modification and sending to {args.ip}:{args.port}...")
        results = processor.process_batch(
            processor.modify_and_send_operation,
            server_ip=args.ip,
            port=args.port,
            ae_title=args.ae_title,
            dicom_tags=dicom_tags
        )
    
    # Return success if more than half of the files were processed successfully
    return 0 if results['success'] >= results['total'] / 2 else 1

if __name__ == "__main__":
    sys.exit(main()) 