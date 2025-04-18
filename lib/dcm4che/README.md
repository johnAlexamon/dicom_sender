# dcm4che Integration

This application now uses the dcm4che Java library for DICOM operations. Follow these steps to set up the library:

## Installation Steps

1. Download the dcm4che library from one of these sources:
   - Official site: https://sourceforge.net/projects/dcm4che/files/dcm4che3/
   - GitHub: https://github.com/dcm4che/dcm4che

2. Extract the downloaded archive

3. Copy the following JAR files to the `lib/dcm4che/lib` directory:
   - `storescu.jar` - For sending DICOM files
   - `echoscu.jar` - For DICOM echo operations
   - Any dependency JAR files needed by these tools

## Verification

To verify the correct installation:

1. Check that the JAR files are present in the correct location
2. Run the application and test the DICOM Echo functionality

## Documentation

- dcm4che storescu documentation: https://github.com/dcm4che/dcm4che/blob/master/dcm4che-tool/dcm4che-tool-storescu/README.md
- dcm4che echoscu documentation: https://github.com/dcm4che/dcm4che/blob/master/dcm4che-tool/dcm4che-tool-echoscu/README.md

## Troubleshooting

If you encounter errors:

1. Verify Java is installed and available in your PATH
2. Check that all required JAR files are in the correct location
3. Examine the log files for specific error messages 