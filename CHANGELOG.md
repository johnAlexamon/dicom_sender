# Changelog

All notable changes to the Alexamon DICOM Sender will be documented in this file.

## [1.4.0] - 2025-04-25

### Added
- Advanced DICOM tag modification using dcm4che3's Attributes API
- Java-based DicomModifier utility for robust tag editing
- Support for modifying PatientID and PatientName tags before sending
- Test script for verifying tag modification functionality
- Setup utility for Java component compilation

### Changed
- Tag modifications now use proper DICOM API instead of command-line arguments
- Improved tag value handling with correct Value Representation (VR)
- Enhanced documentation for tag modification features
- Proper preservation of file meta information during tag modifications

### Fixed
- Fixed issues with special characters in tag values
- Improved cleanup of temporary files
- Better error reporting for failed tag modifications

## [1.3.0] - 2025-04-22

### Added
- Folder selection functionality for sending multiple DICOM files
- Progress tracking UI with status updates during file sending
- Improved error handling and reporting for batch operations

### Changed
- Refactored application to use dcm4che Java library more effectively
- Enhanced user interface for better workflow
- Improved DICOM file detection in folders

### Fixed
- Resolved issues with file path handling on Windows
- Fixed progress display during multiple file transfers
- Improved error messages for common failure scenarios

## [1.2.0] - 2025-04-18

### Added
- New standardized project structure with src directory
- Improved path handling for cross-platform compatibility
- Project rules documentation
- Log file management utility
- Dedicated release folder structure

### Changed
- Reorganized all source code into the src directory
- Improved configuration file handling
- Updated logging to use dedicated logs directory
- Refactored path resolution to be more robust
- Enhanced error handling for file operations

### Fixed
- Fixed path issues with dcm4che library
- Removed duplicate files from root directory
- Improved logging configuration
- Fixed config file loading across different run environments

## [1.1.0] - 2025-04-17

### Added
- Integration with dcm4che Java library
- Support for sending multiple DICOM files
- Progress tracking for multiple file operations
- Folder selection capability

### Changed
- Switched from Python DICOM libraries to dcm4che
- Improved user interface with progress indicators
- Enhanced error handling and reporting

## [1.0.0] - 2025-04-16

### Added
- Initial release
- Basic DICOM file sending functionality
- DICOM echo capability
- Simple user interface with server configuration
- MIT License 