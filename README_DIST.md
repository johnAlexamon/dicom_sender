# Alexamon DICOM Sender

## Overview
Alexamon DICOM Sender is a simple application for sending DICOM files to PACS servers. It provides an easy-to-use interface for configuring server connection settings and sending DICOM images.

## Requirements
- Windows 7/8/10/11
- Java Runtime Environment (JRE) 8 or higher

## How to Use

### 1. Start the Application
- Double-click on `Alexamon_DICOM_Sender.exe` to start the application

### 2. Configure Server Settings
- Enter the PACS server IP address, port, and AE Title in the respective fields
- Click "Save Settings as Default" to store these settings for future use

### 3. Test Connection
- Click the "DICOM Echo" button to test connectivity to the configured PACS server
- A green confirmation message will appear if the echo is successful

### 4. Send DICOM Files
- Click "Select DICOM File" to browse for a DICOM file (.dcm) on your computer
- Once a file is selected, click "Send DICOM" to transmit the file to the PACS server
- The application will display the status of the transmission

### 5. Logs
- All actions are logged to a timestamped log file in the same directory as the application
- The log file path is displayed at the bottom of the application window

## Troubleshooting
- If you see a "Java Runtime not found" message, please install Java from https://www.java.com/
- Ensure that the PACS server is running and accessible from your network
- Check that the AE Title, IP, and port are correctly configured
- Review the log file for detailed error messages

## Licensing
This software is distributed under the MIT License. See LICENSE file for details.

The dcm4che libraries used in this application are licensed under the Mozilla Public License Version 1.1.
For more information, visit: https://github.com/dcm4che/dcm4che/blob/master/LICENSE.txt

## Support
For support, please contact Alexamon or create an issue on the project's GitHub repository.

Copyright © 2025 Alexamon. All rights reserved. 