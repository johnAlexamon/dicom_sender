import customtkinter as ctk
from tkinter import filedialog
import pydicom
from pynetdicom import AE, StoragePresentationContexts, VerificationPresentationContexts
from pynetdicom.sop_class import CTImageStorage
from pynetdicom.pdu_primitives import SCP_SCU_RoleSelectionNegotiation
import os
from pathlib import Path
import logging
import datetime
import json

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
            # Initialize the Application Entity
            ae = AE()
            ae.requested_contexts = VerificationPresentationContexts

            # Get connection parameters
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            ae_title = self.ae_title_entry.get()
            logging.info(f"Attempting DICOM echo to {ip}:{port} with AE Title: {ae_title}")

            # Associate with peer AE
            self.status_label.configure(text="Sending DICOM echo...", text_color="orange")
            assoc = ae.associate(ip, port, ae_title=ae_title)
            
            if assoc.is_established:
                logging.info("Association established successfully")
                # Send the C-ECHO request
                status = assoc.send_c_echo()
                
                if status:
                    success_msg = "DICOM echo successful!"
                    self.status_label.configure(text=success_msg, text_color="green")
                    logging.info(success_msg)
                else:
                    error_msg = "DICOM echo failed!"
                    self.status_label.configure(text=error_msg, text_color="red")
                    logging.error(error_msg)
                
                # Release the association
                assoc.release()
                logging.info("Association released")
            else:
                error_msg = "Failed to establish association with server!"
                self.status_label.configure(text=error_msg, text_color="red")
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
            # Read DICOM file
            logging.info(f"Reading DICOM file: {self.file_path}")
            ds = pydicom.dcmread(self.file_path)
            
            # Log the original transfer syntax
            original_syntax = ds.file_meta.TransferSyntaxUID
            logging.info(f"Original file transfer syntax: {original_syntax}")

            # List of JPEG 2000 transfer syntaxes
            jpeg2000_syntaxes = [
                '1.2.840.10008.1.2.4.90',  # JPEG 2000 Lossless
                '1.2.840.10008.1.2.4.91',  # JPEG 2000 Lossy
            ]

            # Convert to Explicit VR Little Endian if using any JPEG 2000 format
            if original_syntax in jpeg2000_syntaxes:
                logging.info("Converting from JPEG 2000 to Explicit VR Little Endian")
                try:
                    # Decompress pixel data
                    ds.decompress()
                    # Update transfer syntax
                    ds.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian
                    logging.info("Successfully converted to Explicit VR Little Endian")
                except Exception as e:
                    logging.error(f"Failed to decompress image: {str(e)}")
                    raise

            # Initialize the Application Entity
            ae = AE()
            
            # Add CT Image Storage with Explicit VR Little Endian only
            ae.add_requested_context(CTImageStorage, '1.2.840.10008.1.2.1')  # Explicit VR Little Endian
            
            # Get connection parameters
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            ae_title = self.ae_title_entry.get()
            logging.info(f"Attempting to connect to {ip}:{port} with AE Title: {ae_title}")

            # Associate with peer AE
            self.status_label.configure(text="Connecting to server...", text_color="orange")
            assoc = ae.associate(ip, port, ae_title=ae_title)
            
            if assoc.is_established:
                logging.info("Association established successfully")
                # Log accepted presentation contexts
                for context in assoc.accepted_contexts:
                    logging.info(f"Accepted context: {context.abstract_syntax} with transfer syntax: {context.transfer_syntax}")
                
                # Send the DICOM file
                status = assoc.send_c_store(ds)
                
                if status:
                    success_msg = "DICOM file sent successfully!"
                    self.status_label.configure(text=success_msg, text_color="green")
                    logging.info(success_msg)
                else:
                    error_msg = "Failed to send DICOM file!"
                    self.status_label.configure(text=error_msg, text_color="red")
                    logging.error(error_msg)
                
                # Release the association
                assoc.release()
                logging.info("Association released")
            else:
                error_msg = "Failed to establish association with server!"
                self.status_label.configure(text=error_msg, text_color="red")
                logging.error(error_msg)
                # Log rejected presentation contexts
                for context in assoc.rejected_contexts:
                    logging.error(f"Rejected context: {context.abstract_syntax} with transfer syntax: {context.transfer_syntax}")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.status_label.configure(text=error_msg, text_color="red")
            logging.error(f"Exception occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    app = DicomSenderApp()
    app.mainloop() 