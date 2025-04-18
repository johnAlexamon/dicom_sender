"""
Main window for the Alexamon DICOM Sender application
"""

import customtkinter as ctk
from tkinter import filedialog
import pydicom
import os
import logging
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import uuid

from src.utils.config import ConfigManager
from src.utils.file_helpers import find_dicom_files_in_folder
from src.dicom.dcm4che import (
    send_dicom_using_dcm4che, 
    echo_dicom_using_dcm4che, 
    send_multiple_dicom_using_dcm4che,
    send_dicom_using_dcm4che_alt,
    send_multiple_dicom_using_dcm4che_alt
)


class DicomSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load configuration
        self.config_manager = ConfigManager()

        # Configure window
        self.title("Alexamon DICOM Sender")
        self.geometry("600x650")  # Increased height for tag modification UI
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(10, weight=1)  # Adjusted for the progress area

        # Server settings
        self.ip_label = ctk.CTkLabel(self, text="Server IP:")
        self.ip_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ip_entry = ctk.CTkEntry(self)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.ip_entry.insert(0, self.config_manager.get_value("default_ip"))

        self.port_label = ctk.CTkLabel(self, text="Port:")
        self.port_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.port_entry = ctk.CTkEntry(self)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.port_entry.insert(0, self.config_manager.get_value("default_port"))

        self.ae_title_label = ctk.CTkLabel(self, text="AE Title:")
        self.ae_title_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.ae_title_entry = ctk.CTkEntry(self)
        self.ae_title_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.ae_title_entry.insert(0, self.config_manager.get_value("default_ae_title"))

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

        # DICOM Tag Modification Frame
        self.tag_frame = ctk.CTkFrame(self)
        self.tag_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.tag_frame.grid_columnconfigure(0, weight=1)
        self.tag_frame.grid_columnconfigure(1, weight=3)
        
        # Title for the frame
        self.tag_title = ctk.CTkLabel(self.tag_frame, text="DICOM Tag Modification", font=("Arial", 12, "bold"))
        self.tag_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Patient ID modification
        self.patient_id_var = tk.BooleanVar(value=False)
        self.patient_id_check = ctk.CTkCheckBox(self.tag_frame, text="Modify Patient ID (0010,0020):", 
                                              variable=self.patient_id_var, onvalue=True, offvalue=False)
        self.patient_id_check.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.patient_id_entry = ctk.CTkEntry(self.tag_frame)
        self.patient_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Patient Name modification
        self.patient_name_var = tk.BooleanVar(value=False)
        self.patient_name_check = ctk.CTkCheckBox(self.tag_frame, text="Modify Patient Name (0010,0010):", 
                                                variable=self.patient_name_var, onvalue=True, offvalue=False)
        self.patient_name_check.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.patient_name_entry = ctk.CTkEntry(self.tag_frame)
        self.patient_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # DICOM UID Modifications
        self.uid_label = ctk.CTkLabel(self.tag_frame, text="Generate New UIDs:", font=("Arial", 11, "bold"))
        self.uid_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        
        # Study Instance UID (0020,000D)
        self.study_uid_var = tk.BooleanVar(value=False)
        self.study_uid_check = ctk.CTkCheckBox(self.tag_frame, text="Generate New Study UID (0020,000D)", 
                                             variable=self.study_uid_var, onvalue=True, offvalue=False)
        self.study_uid_check.grid(row=4, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        
        # Series Instance UID (0020,000E)
        self.series_uid_var = tk.BooleanVar(value=False)
        self.series_uid_check = ctk.CTkCheckBox(self.tag_frame, text="Generate New Series UID (0020,000E)", 
                                              variable=self.series_uid_var, onvalue=True, offvalue=False)
        self.series_uid_check.grid(row=5, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        
        # SOP Instance UID (0008,0018)
        self.sop_uid_var = tk.BooleanVar(value=False)
        self.sop_uid_check = ctk.CTkCheckBox(self.tag_frame, text="Generate New SOP Instance UID (0008,0018)", 
                                           variable=self.sop_uid_var, onvalue=True, offvalue=False)
        self.sop_uid_check.grid(row=6, column=0, columnspan=2, padx=10, pady=2, sticky="w")

        # Send button - Update row to 9 (was 8)
        self.send_button = ctk.CTkButton(self, text="Send DICOM", command=self.send_dicom)
        self.send_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)
        
        # Progress frame for multiple files - Update row to 10 (was 9)
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
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

        # Status - Update row to 11 (was 10)
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=11, column=0, columnspan=2, padx=10, pady=5)

        # Log file path label - Update row to 12 (was 11)
        from src.utils.file_helpers import get_log_filename
        log_filename = get_log_filename()
        self.log_label = ctk.CTkLabel(self, text=f"Log file: {log_filename}")
        self.log_label.grid(row=12, column=0, columnspan=2, padx=10, pady=5)
        
        # Copyright notice - Update row to 13 (was 12)
        self.copyright_label = ctk.CTkLabel(self, text="© 2025 Alexamon. All rights reserved.", font=("Arial", 10))
        self.copyright_label.grid(row=13, column=0, columnspan=2, padx=10, pady=5)

        logging.info("Alexamon DICOM Sender application started")

    def save_settings(self):
        config = {
            "default_ip": self.ip_entry.get(),
            "default_port": self.port_entry.get(),
            "default_ae_title": self.ae_title_entry.get()
        }
        
        if self.config_manager.save_config(config):
            self.status_label.configure(text="Settings saved as default!", text_color="green")
            logging.info("Default settings saved")
        else:
            self.status_label.configure(text="Failed to save settings!", text_color="red")
            logging.error("Failed to save settings")

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
        self.dicom_files = find_dicom_files_in_folder(folder_path)
        
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
    
    def send_multiple_dicom_thread(self, dicom_tags=None):
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
            self.update_progress,
            dicom_tags
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
        # Get DICOM tag modifications if enabled
        dicom_tags = {}
        if self.patient_id_var.get() and self.patient_id_entry.get():
            dicom_tags["00100020"] = self.patient_id_entry.get()  # PatientID (0010,0020)
        if self.patient_name_var.get() and self.patient_name_entry.get():
            dicom_tags["00100010"] = self.patient_name_entry.get()  # PatientName (0010,0010)
        
        # Handle UID generation if requested
        # Study Instance UID (0020,000D)
        if self.study_uid_var.get():
            new_study_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 10000000}"
            dicom_tags["0020000D"] = new_study_uid
            logging.info(f"Generating new Study UID: {new_study_uid}")
            
        # Series Instance UID (0020,000E)
        if self.series_uid_var.get():
            new_series_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 100000}"
            dicom_tags["0020000E"] = new_series_uid
            logging.info(f"Generating new Series UID: {new_series_uid}")
            
        # SOP Instance UID (0008,0018)
        if self.sop_uid_var.get():
            new_sop_uid = f"1.2.826.0.1.3680043.8.498.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 10000000}.{uuid.uuid4().int % 1000000}"
            dicom_tags["00080018"] = new_sop_uid
            logging.info(f"Generating new SOP Instance UID: {new_sop_uid}")
            
        # Check if we have a folder selection
        if self.folder_path and self.dicom_files:
            if len(self.dicom_files) == 0:
                self.status_label.configure(text="No DICOM files found in the selected folder!", text_color="red")
                return
                
            # Log tag modifications if any
            if dicom_tags:
                tag_str = ", ".join([f"{k}={v}" for k, v in dicom_tags.items()])
                logging.info(f"Will modify DICOM tags: {tag_str}")
                
            # Start thread to send multiple files, using the alternative function
            threading.Thread(target=lambda: self.send_multiple_dicom_thread_alt(dicom_tags), daemon=True).start()
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
                
                # Log original tag values if modifications are requested
                if dicom_tags:
                    # PatientID (0010,0020)
                    if "00100020" in dicom_tags and hasattr(ds, "PatientID"):
                        logging.info(f"Original PatientID: {ds.PatientID}, will change to: {dicom_tags['00100020']}")
                    # PatientName (0010,0010)
                    if "00100010" in dicom_tags and hasattr(ds, "PatientName"):
                        logging.info(f"Original PatientName: {ds.PatientName}, will change to: {dicom_tags['00100010']}")
                    
                    tag_str = ", ".join([f"{k}={v}" for k, v in dicom_tags.items()])
                    logging.info(f"Will modify DICOM tags: {tag_str}")
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
            
            # Send DICOM using dcm4che, including tag modifications if any, using the alternative function
            result = send_dicom_using_dcm4che_alt(self.file_path, ip, port, ae_title, dicom_tags)
            
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

    def send_multiple_dicom_thread_alt(self, dicom_tags=None):
        """Thread function to send multiple DICOM files using the alternative implementation"""
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
        
        # Send the files using the alternative implementation
        results = send_multiple_dicom_using_dcm4che_alt(
            self.dicom_files, 
            ip, 
            port, 
            ae_title, 
            self.update_progress,
            dicom_tags
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