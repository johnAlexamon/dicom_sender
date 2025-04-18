# Changelog

All notable changes to the Alexamon DICOM Sender will be documented in this file.

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