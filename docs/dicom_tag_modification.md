# DICOM Tag Modification

This document explains how to use the DICOM tag modification feature in the Alexamon DICOM Sender application.

## Overview

The DICOM tag modification feature allows you to modify DICOM attributes (tags) before sending DICOM files to a PACS server. This is useful for:

- Anonymizing patient data
- Correcting erroneous tags
- Testing PACS server behavior with different tag values
- Research and educational purposes

The implementation uses dcm4che3's native Java API for tag modification, ensuring proper handling of DICOM Value Representations (VR) and preserving file meta information.

## How It Works

When you select tags to modify in the application:

1. The original DICOM file is read using dcm4che3's DicomInputStream
2. Tags are modified in memory using the Attributes class
3. A temporary modified copy is created and sent to the PACS
4. The original file remains untouched
5. Temporary files are cleaned up after sending

## Using Tag Modification in the GUI

1. Launch the Alexamon DICOM Sender application
2. Configure your server settings (IP, Port, AE Title)
3. Select a DICOM file or folder containing DICOM files
4. In the "DICOM Tag Modification" section:
   - Check the box next to "Modify Patient ID" and/or "Modify Patient Name"
   - Enter the new values in the corresponding text fields
5. Click "Send DICOM" to send the modified file(s)

The application will:
- Create a temporary copy of each file with the modified tags
- Send the modified files to the PACS server
- Delete the temporary files when done
- Log the modifications in the application log

## Available Tags for Modification

Currently, the GUI supports modifying these common tags:

- Patient ID (0010,0020)
- Patient Name (0010,0010)

## Testing Tag Modification

For testing and verification purposes, you can use the included test script:

```bash
python scripts/test_dicom_tag_modification.py --file path/to/dicom.dcm --tag "0010,0020=ANONYMOUS" --tag "0010,0010=ANONYMOUS^PATIENT"
```

This script will:
1. Display the original tag values
2. Modify the specified tags
3. Display the modified tag values
4. Show the path to the modified file

## Technical Implementation

### Java DicomModifier Utility

The core of the tag modification feature is the `DicomModifier.java` utility located in `src/java/`. This utility:

1. Reads DICOM files using dcm4che3's DicomInputStream
2. Modifies specified tags while preserving proper VR and file meta information
3. Writes the modified dataset to a new file
4. Provides clear error reporting

### Integration with Python

The tag modification is integrated with the Python application through:

1. `src/dicom/dicom_modifier.py` - Python interface to the Java utility
2. `src/dicom/dcm4che.py` - Updated to use tag modification before sending
3. `scripts/setup_dcm4che_modifier.bat` - Sets up the Java environment

### Building the DicomModifier Utility

The Java utility needs to be compiled before use. This is automatically handled by:

```bash
scripts/setup_dcm4che_modifier.bat
```

This script validates your dcm4che setup and compiles the Java utility.

## Troubleshooting

If you encounter issues with tag modification:

1. Check the application logs for detailed error messages
2. Run the setup script to ensure the Java utility is properly compiled:
   ```bash
   scripts/setup_dcm4che_modifier.bat
   ```
3. Verify your dcm4che setup is complete with all required JAR files
4. Ensure Java is installed and properly configured

## Advanced Usage: Custom Tag Modifications

While the GUI currently supports modifying Patient ID and Patient Name, the underlying implementation supports modifying any DICOM tag. For advanced users, the test script can be used to modify any tag:

```bash
python scripts/test_dicom_tag_modification.py --file path/to/dicom.dcm --tag "00080020=20250425" --tag "00080030=123000"
```

In this example, we're modifying the Study Date and Study Time tags.

## Future Enhancements

We plan to extend the tag modification feature in future releases:

- Support for more DICOM tags in the GUI
- Batch anonymization profiles
- DICOM tag templates for common modifications
- Tag modification preview
- Support for more complex tag modifications 