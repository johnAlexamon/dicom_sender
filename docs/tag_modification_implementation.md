# DICOM Tag Modification Implementation Guide

This document outlines the steps to implement and integrate the DICOM tag modification feature into your project.

## Implementation Steps

1. **Setup the Java Environment**
   - Ensure Java is installed on your system
   - Run `scripts/setup_dcm4che_modifier.bat` to verify dcm4che installation and compile the Java utility

2. **File Structure**
   - `src/java/DicomModifier.java` - Java utility for modifying DICOM tags
   - `src/java/build.bat` - Script to compile the Java utility
   - `src/java/run_dicom_modifier.bat` - Script to run the Java utility
   - `src/dicom/dicom_modifier.py` - Python interface to the Java utility
   - `scripts/test_dicom_tag_modification.py` - Test script for tag modification
   - `docs/dicom_tag_modification.md` - Documentation for the feature

3. **Testing the Implementation**
   - Run the validation script: `python -m src.utils.dcm4che_validator`
   - Test tag modification: `python scripts/test_dicom_tag_modification.py --file path/to/dicom.dcm --tag "0010,0020=ANONYMOUS"`
   - Verify the modified file has the expected changes

4. **Integration with the DICOM Sender**
   - The main application already uses the new tag modification feature
   - Tags specified in the UI will be modified before sending
   - Check the application logs for verification

## How It Works - Technical Details

### Java Component

1. The Java `DicomModifier` uses dcm4che3's API to:
   - Read the DICOM file with `DicomInputStream`
   - Get the file's meta information
   - Modify the required tags using `Attributes.setString()`
   - Write the modified file with `DicomOutputStream`

2. The Java utility handles the correct Value Representation (VR) for each tag:
   - Automatically detects the VR from the existing attributes
   - Uses appropriate defaults when necessary (PN for Patient Name, LO for others)

### Python Integration

1. The `dicom_modifier.py` module:
   - Provides a simple interface to call the Java utility
   - Handles temporary file management
   - Logs all operations and errors

2. Integration in `dcm4che.py`:
   - Each sending function now checks for tag modifications
   - If modifications are requested, it creates a modified copy before sending
   - Cleans up temporary files after sending

### Command Line Interface

The test script provides a command-line interface for tag modification:
```
python scripts/test_dicom_tag_modification.py --file <dicom_file> --tag "<tag>=<value>" [--tag "<tag>=<value>" ...]
```

Where:
- `<dicom_file>` is the path to a DICOM file
- `<tag>` is a DICOM tag in the format "00100020" or "0010,0020"
- `<value>` is the new value for the tag

## Troubleshooting

1. **Java Compilation Issues:**
   - Check Java installation: `java -version`
   - Verify dcm4che JAR files are in the correct location
   - Check the build script output for errors

2. **Tag Modification Errors:**
   - Invalid tag format (use 8-hex-digits format, e.g., "00100020")
   - File access issues (read/write permissions)
   - DICOM format issues (corrupted files)

3. **Integration Issues:**
   - Check application logs for detailed error messages
   - Verify the Java utility is properly compiled
   - Make sure temporary directories are writable

## Future Development

Future versions may include:
1. Support for more tag types in the UI
2. Anonymization profiles for common use cases
3. Batch tag modification options
4. Tag validation rules
5. Preview of modifications before sending 