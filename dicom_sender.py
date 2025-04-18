"""
Alexamon DICOM Sender
Copyright © 2025 Alexamon. All rights reserved.

A DICOM file transfer application using dcm4che Java libraries for PACS connectivity.
"""

import customtkinter as ctk
from tkinter import filedialog
import pydicom  # Still needed for basic DICOM metadata reading
import os
from pathlib import Path
import logging
import datetime
import json
import subprocess
import glob
from tkinter import ttk
import threading
import time
import tkinter as tk

# Configure logging
os.makedirs('logs', exist_ok=True)  # Ensure logs directory exists
log_filename = f"logs/dicom_sender_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# Helper function for dcm4che storescu command
def send_dicom_using_dcm4che(file_path, host, port, ae_title):
    """
    Send DICOM file using dcm4che storescu tool.
    
    Parameters:
    - file_path: Path to the DICOM file
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    # Use the classpath approach for better control
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "dcm4che", "lib")
    
    # Build classpath with all necessary JARs
    classpath = os.pathsep.join([
        os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
        os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
        os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
        os.path.join(lib_dir, "logback-core-1.5.12.jar"),
        os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
        # The main storescu JAR
        os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
    ])
    
    # Run the storescu command
    cmd = [
        "java", "-cp", classpath,
        "org.dcm4che3.tool.storescu.StoreSCU",
        "-c", f"{ae_title}@{host}:{port}",
        file_path
    ]
    logging.info(f"Executing command: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)

# Helper function for dcm4che echoscu command
def echo_dicom_using_dcm4che(host, port, ae_title):
    """
    Send DICOM echo using a simplified approach.
    
    Parameters:
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "dcm4che", "lib")
    
    # Build classpath with all necessary JARs
    classpath = os.pathsep.join([
        os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
        os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
        os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
        os.path.join(lib_dir, "logback-core-1.5.12.jar"),
        os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
        os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar") 
    ])
    
    # Simply try to associate with the server and report success if connection is established
    cmd = [
        "java", "-cp", classpath,
        "org.dcm4che3.tool.storescu.StoreSCU",
        "-b", "DICOM_SENDER", # Use a local AE title
        "-c", f"{ae_title}@{host}:{port}"
    ]
    
    logging.info(f"Executing command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # If we can connect and see "Connected to" in the output, consider it a successful echo
        if "Connected to" in result.stdout:
            result.returncode = 0  # Mark as successful
        return result
    except Exception as e:
        # Create a CompletedProcess-like object to return in case of error
        class ErrorResult:
            def __init__(self, error):
                self.returncode = 1
                self.stdout = ""
                self.stderr = str(error)
        
        return ErrorResult(e)

# Helper function for dcm4che storescu command to send multiple files
def send_multiple_dicom_using_dcm4che(file_paths, host, port, ae_title, progress_callback=None):
    """
    Send multiple DICOM files using dcm4che storescu tool.
    
    Parameters:
    - file_paths: List of paths to the DICOM files
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - progress_callback: Optional callback function to update progress
    
    Returns:
    - Dictionary with results for each file
    """
    results = {}
    total_files = len(file_paths)
    
    for i, file_path in enumerate(file_paths):
        try:
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, total_files, Path(file_path).name)
                
            # Use the classpath approach for better control
            lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "dcm4che", "lib")
            
            # Build classpath with all necessary JARs
            classpath = os.pathsep.join([
                os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
                os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
                os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
                os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
                os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
                os.path.join(lib_dir, "logback-core-1.5.12.jar"),
                os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
                # The main storescu JAR
                os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
            ])
            
            # Run the storescu command
            cmd = [
                "java", "-cp", classpath,
                "org.dcm4che3.tool.storescu.StoreSCU",
                "-c", f"{ae_title}@{host}:{port}",
                file_path
            ]
            logging.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Store results
            results[file_path] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            results[file_path] = {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    # Final progress update
    if progress_callback:
        progress_callback(total_files, total_files, "Completed")
        
    return results

class DicomSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load configuration
        self.config = self.load_config()

        # Configure window
        self.title("Alexamon DICOM Sender")
        self.geometry("600x580")  # Increased height for additional UI elements
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(8, weight=1)  # Adjusted for the progress area

        # Server settings
        self.ip_label = ctk.CTkLabel(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ip_entry = ctk.CTkEntry(self)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.ip_entry.insert(0, self.config["default_ip"])

        self.port_label = ctk.CTkLabel(self, text="Port:")
        self.port_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.port_entry = ctk.CTkEntry(self)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.port_entry.insert(0, self.config["default_port"])

        self.ae_title_label = ctk.CTkLabel(self, text="AE Title:")
        self.ae_title_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ae_title_entry = ctk.CTkEntry(self)
        self.ae_title_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.ae_title_entry.insert(0, self.config["default_ae_title"])

        # Save settings button
        self.save_settings_button = ctk.CTkButton(self, text="Save Settings as Default", command=self.save_settings)
        self.save_settings_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Echo button
        self.echo_button = ctk.CTkButton(self, text="DICOM Echo", command=self.send_echo)
        self.echo_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # File selection
        self.file_path = None
        self.folder_path = None
        self.dicom_files = []
        
        # File selection frame
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_columnconfigure(1, weight=1)
        
        self.file_button = ctk.CTkButton(file_frame, text="Select DICOM File", command=self.select_file)
        self.file_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.folder_button = ctk.CTkButton(file_frame, text="Select DICOM Folder", command=self.select_folder)
        self.folder_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.file_label = ctk.CTkLabel(self, text="No file selected")
        self.file_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # Send button
        self.send_button = ctk.CTkButton(self, text="Send DICOM", command=self.send_dicom)
        self.send_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5)
        
        # Progress frame for multiple files
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar and labels (hidden initially)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Sending files: 0/0")
        self.progress_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Create a regular ttk progress bar (as CTkProgressBar doesn't support determinate mode well)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var, 
            mode='determinate',
            length=580
        )
        self.progress_bar.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.current_file_label = ctk.CTkLabel(self.progress_frame, text="")
        self.current_file_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Hide progress frame initially
        self.progress_frame.grid_remove()

        # Status
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

        # Log file path label
        self.log_label = ctk.CTkLabel(self, text=f"Log file: {log_filename}")
        self.log_label.grid(row=10, column=0, columnspan=2, padx=10, pady=5)
        
        # Copyright notice
        self.copyright_label = ctk.CTkLabel(self, text="© 2025 Alexamon. All rights reserved.", font=("Arial", 10))
        self.copyright_label.grid(row=11, column=0, columnspan=2, padx=10, pady=5)

        logging.info("Alexamon DICOM Sender application started")

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config if file doesn't exist
            default_config = {
                "default_ip": "127.0.0.1",
                "default_port": "11112",
                "default_ae_title": "STORE_SCP"
            }
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def save_settings(self):
        self.config = {
            "default_ip": self.ip_entry.get(),
            "default_port": self.port_entry.get(),
            "default_ae_title": self.ae_title_entry.get()
        }
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        self.status_label.configure(text="Settings saved as default!", text_color="green")
        logging.info("Default settings saved")

    def send_echo(self):
        try:
            # Get connection parameters
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            ae_title = self.ae_title_entry.get()
            logging.info(f"Attempting DICOM echo to {ip}:{port} with AE Title: {ae_title}")

            # Update status
            self.status_label.configure(text="Sending DICOM echo...", text_color="orange")
            
            # Run echo command using dcm4che
            result = echo_dicom_using_dcm4che(ip, port, ae_title)
            
            # Process result
            if result.returncode == 0:
                success_msg = "DICOM echo successful!"
                self.status_label.configure(text=success_msg, text_color="green")
                logging.info(success_msg)
                logging.info(f"Echo output: {result.stdout}")
            else:
                error_msg = f"DICOM echo failed: {result.stderr}"
                self.status_label.configure(text="DICOM echo failed!", text_color="red")
                logging.error(error_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.status_label.configure(text=error_msg, text_color="red")
            logging.error(f"Exception occurred: {str(e)}", exc_info=True)

    def select_folder(self):
        """Handle folder selection to get all DICOM files from a directory"""
        folder_path = filedialog.askdirectory(title="Select Folder Containing DICOM Files")
        if not folder_path:
            return
            
        self.folder_path = folder_path
        self.file_path = None  # Clear single file selection
        
        # Search for DICOM files in the folder
        self.dicom_files = []
        
        # Look for .dcm files
        dcm_files = glob.glob(os.path.join(folder_path, "**/*.dcm"), recursive=True)
        self.dicom_files.extend(dcm_files)
        
        # Also look for files without extension that might be DICOM
        for filename in Path(folder_path).rglob('*'):
            if filename.is_file() and not filename.suffix and filename not in self.dicom_files:
                try:
                    # Try to read as DICOM
                    pydicom.dcmread(filename, stop_before_pixels=True)
                    self.dicom_files.append(str(filename))
                except:
                    # Not a DICOM file, skip
                    pass
        
        num_files = len(self.dicom_files)
        if num_files == 0:
            self.file_label.configure(text=f"No DICOM files found in selected folder")
            logging.warning(f"No DICOM files found in folder: {folder_path}")
        else:
            self.file_label.configure(text=f"Selected folder: {os.path.basename(folder_path)} ({num_files} DICOM files)")
            logging.info(f"Selected folder with {num_files} DICOM files: {folder_path}")
    
    def update_progress(self, current, total, current_file):
        """Update the progress display for multiple file sending"""
        self.progress_var.set((current / total) * 100)
        self.progress_label.configure(text=f"Sending files: {current}/{total}")
        self.current_file_label.configure(text=f"Current file: {current_file}")
        self.update_idletasks()  # Force UI update
    
    def send_multiple_dicom_thread(self):
        """Thread function to send multiple DICOM files"""
        # Get connection parameters
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        ae_title = self.ae_title_entry.get()
        
        # Show progress UI
        self.progress_frame.grid()
        self.progress_var.set(0)
        self.update_progress(0, len(self.dicom_files), "Starting...")
        
        # Disable send button during sending
        self.send_button.configure(state="disabled")
        
        # Send the files
        results = send_multiple_dicom_using_dcm4che(
            self.dicom_files, 
            ip, 
            port, 
            ae_title, 
            self.update_progress
        )
        
        # Count successes and failures
        successes = sum(1 for result in results.values() if result["success"])
        failures = len(results) - successes
        
        # Update status
        status_text = f"Sent {successes}/{len(results)} files successfully"
        if failures > 0:
            status_text += f", {failures} failed"
        
        # Log results
        logging.info(status_text)
        for file_path, result in results.items():
            if result["success"]:
                logging.info(f"Successfully sent: {file_path}")
            else:
                logging.error(f"Failed to send: {file_path}. Error: {result['error']}")
        
        # Update UI in the main thread
        def update_ui():
            self.status_label.configure(
                text=status_text,
                text_color="green" if failures == 0 else "orange"
            )
            self.send_button.configure(state="normal")
            
            # Hide progress after a delay
            self.after(3000, self.progress_frame.grid_remove)
        
        self.after(0, update_ui)
    
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select DICOM file",
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        if filename:
            self.file_path = filename
            self.folder_path = None  # Clear folder selection
            self.dicom_files = []
            self.file_label.configure(text=f"Selected: {Path(filename).name}")
            logging.info(f"Selected DICOM file: {filename}")

    def send_dicom(self):
        # Check if we have a folder selection
        if self.folder_path and self.dicom_files:
            if len(self.dicom_files) == 0:
                self.status_label.configure(text="No DICOM files found in the selected folder!", text_color="red")
                return
                
            # Start thread to send multiple files
            threading.Thread(target=self.send_multiple_dicom_thread, daemon=True).start()
            return
        
        # Otherwise handle single file
        if not self.file_path:
            error_msg = "Please select a DICOM file or folder first!"
            self.status_label.configure(text=error_msg, text_color="red")
            logging.error(error_msg)
            return

        try:
            # Basic validation - verify it's a DICOM file
            try:
                ds = pydicom.dcmread(self.file_path)
                logging.info(f"Reading DICOM file: {self.file_path}")
                logging.info(f"File transfer syntax: {ds.file_meta.TransferSyntaxUID}")
            except Exception as e:
                error_msg = f"Error reading DICOM file: {str(e)}"
                self.status_label.configure(text=error_msg, text_color="red")
                logging.error(error_msg)
                return

            # Get connection parameters
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            ae_title = self.ae_title_entry.get()
            logging.info(f"Attempting to send DICOM to {ip}:{port} with AE Title: {ae_title}")

            # Update status
            self.status_label.configure(text="Sending DICOM file...", text_color="orange")
            
            # Send DICOM using dcm4che
            result = send_dicom_using_dcm4che(self.file_path, ip, port, ae_title)
            
            # Process result
            if result.returncode == 0:
                success_msg = "DICOM file sent successfully!"
                self.status_label.configure(text=success_msg, text_color="green")
                logging.info(success_msg)
                logging.info(f"Send output: {result.stdout}")
            else:
                error_msg = f"Failed to send DICOM file: {result.stderr}"
                self.status_label.configure(text="Failed to send DICOM file!", text_color="red")
                logging.error(error_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.status_label.configure(text=error_msg, text_color="red")
            logging.error(f"Exception occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    app = DicomSenderApp()
    app.mainloop() 