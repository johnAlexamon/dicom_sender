import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_dcm4che():
    """Download and extract dcm4che library JAR files"""
    print("Downloading dcm4che library...")
    
    # Create necessary directories
    os.makedirs("lib/dcm4che/lib", exist_ok=True)
    
    # Download URL (latest stable version from SourceForge)
    version = "5.33.1"  # Latest version based on search results
    download_url = f"https://sourceforge.net/projects/dcm4che/files/dcm4che3/{version}/dcm4che-{version}-bin.zip/download"
    zip_path = "dcm4che.zip"
    
    try:
        # Download the file
        print(f"Downloading from {download_url}...")
        urllib.request.urlretrieve(download_url, zip_path)
        print("Download complete!")
        
        # Extract the zip file
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_dcm4che")
        
        # Copy the necessary JAR files
        print("Copying JAR files...")
        dcm4che_dir = f"temp_dcm4che/dcm4che-{version}"
        
        # Copy echoscu.jar and its dependencies
        shutil.copy(os.path.join(dcm4che_dir, "bin", "echoscu.jar"), "lib/dcm4che/lib/")
        shutil.copy(os.path.join(dcm4che_dir, "lib", f"dcm4che-core-{version}.jar"), "lib/dcm4che/lib/")
        shutil.copy(os.path.join(dcm4che_dir, "lib", f"dcm4che-net-{version}.jar"), "lib/dcm4che/lib/")
        shutil.copy(os.path.join(dcm4che_dir, "lib", f"dcm4che-tool-common-{version}.jar"), "lib/dcm4che/lib/")
        
        # Copy SLF4J and logback dependencies (version might be different)
        # Will copy all JAR files that match the pattern
        for jar_file in os.listdir(os.path.join(dcm4che_dir, "lib")):
            if jar_file.startswith(("slf4j", "logback")):
                shutil.copy(os.path.join(dcm4che_dir, "lib", jar_file), "lib/dcm4che/lib/")
        
        # Copy storescu.jar
        shutil.copy(os.path.join(dcm4che_dir, "bin", "storescu.jar"), "lib/dcm4che/lib/")
        
        # Clean up
        print("Cleaning up...")
        os.remove(zip_path)
        shutil.rmtree("temp_dcm4che")
        
        print("dcm4che library setup complete!")
        print("You can now run the application with: python dicom_sender.py")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    download_dcm4che() 