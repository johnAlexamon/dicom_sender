import os
import logging
import subprocess
from pathlib import Path
from src.utils.file_helpers import get_lib_dir

def validate_dcm4che_setup():
    """
    Validate that the dcm4che library is properly set up.
    Checks for required JAR files and generates a report.
    
    Returns:
    - tuple: (is_valid, report_message)
    """
    logging.info("Validating dcm4che setup...")
    
    # List of required JAR files
    required_jars = [
        "dcm4che-core-5.33.1.jar",
        "dcm4che-net-5.33.1.jar",
        "dcm4che-tool-common-5.33.1.jar",
        "commons-cli-1.9.0.jar",
        "slf4j-api-2.0.16.jar",
        "logback-core-1.5.12.jar",
        "logback-classic-1.5.12.jar",
        "dcm4che-tool-storescu-5.33.1.jar"
    ]
    
    # Get the library directory path
    lib_dir = get_lib_dir()
    logging.info(f"Checking for JAR files in: {lib_dir}")
    
    # Check if the directory exists
    if not os.path.exists(lib_dir):
        return False, f"Library directory not found: {lib_dir}"
    
    # Check for each required JAR file
    missing_jars = []
    found_jars = []
    
    for jar_file in required_jars:
        jar_path = os.path.join(lib_dir, jar_file)
        if os.path.exists(jar_path):
            found_jars.append(jar_file)
            logging.info(f"Found JAR file: {jar_file}")
        else:
            missing_jars.append(jar_file)
            logging.warning(f"Missing JAR file: {jar_file}")
    
    # Build report message
    if missing_jars:
        report = f"Missing {len(missing_jars)} required JAR files:\n"
        for jar in missing_jars:
            report += f"- {jar}\n"
        report += f"\nFound {len(found_jars)} JAR files:\n"
        for jar in found_jars:
            report += f"- {jar}\n"
        is_valid = False
    else:
        report = f"All required JAR files found in {lib_dir}!\n"
        for jar in found_jars:
            report += f"- {jar}\n"
        is_valid = True
    
    # Check if Java is installed
    try:
        java_version = subprocess.run(
            ["java", "-version"], 
            capture_output=True, 
            text=True
        )
        if java_version.returncode == 0:
            java_info = java_version.stderr.strip()  # Java outputs version to stderr
            report += f"\nJava is installed: {java_info}\n"
            logging.info(f"Java is installed: {java_info}")
        else:
            report += "\nWarning: Java may not be properly installed!\n"
            logging.warning("Java may not be properly installed")
            is_valid = False
    except Exception as e:
        report += f"\nError checking Java installation: {str(e)}\n"
        logging.error(f"Error checking Java installation: {str(e)}")
        is_valid = False
    
    # If everything is valid, check/build the DicomModifier utility
    if is_valid:
        dicom_modifier_status = check_build_dicom_modifier()
        report += dicom_modifier_status
    
    return is_valid, report

def check_build_dicom_modifier():
    """
    Check if the DicomModifier utility is built and build it if necessary
    
    Returns:
    - str: Status message about the DicomModifier
    """
    # Get path to the Java source file
    java_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "java")
    source_file = os.path.join(java_dir, "DicomModifier.java")
    class_file = os.path.join(java_dir, "DicomModifier.class")
    
    # If the source file doesn't exist, return a warning
    if not os.path.exists(source_file):
        return "\nWarning: DicomModifier.java source file not found!\n"
    
    # If the class file exists and is newer than the source file, no need to rebuild
    if os.path.exists(class_file) and os.path.getmtime(class_file) > os.path.getmtime(source_file):
        return "\nDicomModifier utility is already built.\n"
    
    # Otherwise, build the utility
    logging.info("Building DicomModifier utility...")
    build_script = os.path.join(java_dir, "build.bat")
    
    if not os.path.exists(build_script):
        return "\nWarning: DicomModifier build script not found!\n"
    
    try:
        result = subprocess.run(build_script, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info("Successfully built DicomModifier utility")
            return "\nSuccessfully built DicomModifier utility.\n"
        else:
            error_message = result.stderr or result.stdout or "Unknown error"
            logging.error(f"Failed to build DicomModifier: {error_message}")
            return f"\nFailed to build DicomModifier: {error_message}\n"
    except Exception as e:
        logging.error(f"Error building DicomModifier: {str(e)}")
        return f"\nError building DicomModifier: {str(e)}\n"

def find_dcm4che_jars():
    """
    Attempt to find dcm4che JAR files in common locations.
    
    Returns:
    - list of paths where JAR files were found
    """
    possible_locations = [
        os.path.join(os.path.expanduser("~"), "dcm4che"),
        os.path.join(os.path.expanduser("~"), "Downloads", "dcm4che"),
        r"C:\dcm4che",
        r"C:\Program Files\dcm4che",
        r"C:\Program Files (x86)\dcm4che",
        r"D:\dcm4che"
    ]
    
    found_locations = []
    
    for location in possible_locations:
        if os.path.exists(location):
            # Walk through directory to find JAR files
            for root, dirs, files in os.walk(location):
                jar_files = [f for f in files if f.endswith(".jar") and "dcm4che" in f]
                if jar_files:
                    found_locations.append(root)
                    logging.info(f"Found dcm4che JAR files in: {root}")
    
    return found_locations

def suggest_download_commands():
    """
    Generate PowerShell commands to download the dcm4che distribution.
    
    Returns:
    - str: PowerShell commands to download and extract dcm4che
    """
    commands = """
# PowerShell commands to download and extract dcm4che:

# Create directory for dcm4che
$dcm4cheDir = "C:\\dcm4che"
New-Item -ItemType Directory -Force -Path $dcm4cheDir

# Download dcm4che
$url = "https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.33.1/dcm4che-5.33.1-bin.zip/download"
$output = "$dcm4cheDir\\dcm4che-5.33.1-bin.zip"
Invoke-WebRequest -Uri $url -OutFile $output

# Extract the zip file
Expand-Archive -Path $output -DestinationPath $dcm4cheDir

# Copy the JAR files to the lib directory
$libDir = "{lib_dir}"
New-Item -ItemType Directory -Force -Path $libDir

# Copy required JAR files
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\dcm4che-core-5.33.1.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\dcm4che-net-5.33.1.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\dcm4che-tool-common-5.33.1.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\commons-cli-1.9.0.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\slf4j-api-2.0.16.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\logback-core-1.5.12.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\logback-classic-1.5.12.jar" -Destination $libDir
Copy-Item "$dcm4cheDir\\dcm4che-5.33.1\\lib\\dcm4che-tool-storescu-5.33.1.jar" -Destination $libDir

Write-Host "dcm4che has been downloaded and JARs copied to $libDir"
""".format(lib_dir=get_lib_dir())
    
    return commands

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Validate dcm4che setup
    is_valid, report = validate_dcm4che_setup()
    
    print("\n=== DCM4CHE SETUP VALIDATION REPORT ===")
    print(report)
    
    if not is_valid:
        print("\n=== SEARCHING FOR DCM4CHE JAR FILES ===")
        found_locations = find_dcm4che_jars()
        
        if found_locations:
            print("\nFound dcm4che JAR files in the following locations:")
            for location in found_locations:
                print(f"- {location}")
            print("\nYou may need to copy these JAR files to the library directory.")
        else:
            print("\nNo dcm4che JAR files found in common locations.")
            print("\nYou can download dcm4che and set it up using these commands:")
            print(suggest_download_commands()) 