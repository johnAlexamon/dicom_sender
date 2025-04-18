import customtkinter as ctk
from tkinter import filedialog
import pydicom  # Still needed for basic DICOM metadata reading
import os
from pathlib import Path
import logging
import datetime
import json
import subprocess

# Configure logging
log_filename = f"dicom_sender_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    # Path to dcm4che jar file - update this to your actual path
    jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "dcm4che", "lib", "storescu.jar")
    
    cmd = [
        "java", "-jar", jar_path,
        "-c", f"{ae_title}@{host}:{port}",
        file_path
    ]
    logging.info(f"Executing command: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)

# Helper function for dcm4che echoscu command
def echo_dicom_using_dcm4che(host, port, ae_title):
    """
    Send DICOM echo using dcm4che echoscu tool.
    
    Parameters:
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    # Path to dcm4che jar file - update this to your actual path
    jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib", "dcm4che", "lib", "echoscu.jar")
    
    cmd = [
        "java", "-jar", jar_path,
        "-c", f"{ae_title}@{host}:{port}"
    ]
    logging.info(f"Executing command: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)

class DicomSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load configuration
        self.config = self.load_config()

        # Configure window
        self.title("DICOM Sender")
        self.geometry("600x500")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

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
        self.file_button = ctk.CTkButton(self, text="Select DICOM File", command=self.select_file)
        self.file_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.file_label = ctk.CTkLabel(self, text="No file selected")
        self.file_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # Send button
        self.send_button = ctk.CTkButton(self, text="Send DICOM", command=self.send_dicom)
        self.send_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Status
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        # Log file path label
        self.log_label = ctk.CTkLabel(self, text=f"Log file: {log_filename}")
        self.log_label.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

        logging.info("DICOM Sender application started")

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

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select DICOM file",
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        if filename:
            self.file_path = filename
            self.file_label.configure(text=f"Selected: {Path(filename).name}")
            logging.info(f"Selected DICOM file: {filename}")

    def send_dicom(self):
        if not self.file_path:
            error_msg = "Please select a DICOM file first!"
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