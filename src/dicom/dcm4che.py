"""
DICOM operations using dcm4che Java libraries
"""

import os
import subprocess
import logging
from pathlib import Path
from src.utils.file_helpers import get_lib_dir
from src.dicom.dicom_modifier import modify_dicom_tags, cleanup_temp_files

def send_dicom_using_dcm4che(file_path, host, port, ae_title, dicom_tags=None):
    """
    Send DICOM file using dcm4che storescu tool.
    
    Parameters:
    - file_path: Path to the DICOM file
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    # If we have tags to modify, use the Java-based modifier
    temp_file = None
    if dicom_tags and isinstance(dicom_tags, dict):
        modified_file = modify_dicom_tags(file_path, dicom_tags)
        if modified_file:
            temp_file = modified_file
            file_path = modified_file
            logging.info(f"Using modified DICOM file: {file_path}")
        else:
            logging.warning("Failed to modify DICOM tags, proceeding with original file")
    
    try:
        # Use the classpath approach for better control
        lib_dir = get_lib_dir()
        
        # Build classpath with all necessary JARs
        classpath = os.pathsep.join([
            os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
            os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
            os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
            os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
            os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
            os.path.join(lib_dir, "logback-core-1.5.12.jar"),
            os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
            # The main storescu JAR
            os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
        ])
        
        # Build the command - no longer need tag modification options
        cmd = [
            "java", "-cp", classpath,
            "org.dcm4che3.tool.storescu.StoreSCU",
            "-c", f"{ae_title}@{host}:{port}",
            "--", # Add a separator to indicate end of options
            file_path
        ]
        
        logging.info(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temporary file if we created one
        if temp_file:
            cleanup_temp_files(temp_file)
            
        return result
        
    except Exception as e:
        # Clean up temporary file if an exception occurred
        if temp_file:
            cleanup_temp_files(temp_file)
        raise e

def send_dicom_using_dcm4che_alt(file_path, host, port, ae_title, dicom_tags=None):
    """
    Alternative implementation of the DICOM sender using shell=True for complex command handling.
    
    Parameters:
    - file_path: Path to the DICOM file
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    # If we have tags to modify, use the Java-based modifier
    temp_file = None
    if dicom_tags and isinstance(dicom_tags, dict):
        modified_file = modify_dicom_tags(file_path, dicom_tags)
        if modified_file:
            temp_file = modified_file
            file_path = modified_file
            logging.info(f"Using modified DICOM file: {file_path}")
        else:
            logging.warning("Failed to modify DICOM tags, proceeding with original file")
    
    try:
        # Use the classpath approach for better control
        lib_dir = get_lib_dir()
        
        # Build classpath with all necessary JARs
        classpath = os.pathsep.join([
            os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
            os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
            os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
            os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
            os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
            os.path.join(lib_dir, "logback-core-1.5.12.jar"),
            os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
            os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
        ])
        
        # Convert file path to absolute path with normalized slashes
        abs_file_path = os.path.abspath(file_path).replace('\\', '/')
        
        # Build command parts for better control
        cmd_parts = []
        cmd_parts.append('java')
        cmd_parts.append('-cp')
        cmd_parts.append(f'"{classpath}"')
        cmd_parts.append('org.dcm4che3.tool.storescu.StoreSCU')
        cmd_parts.append('-c')
        cmd_parts.append(f'{ae_title}@{host}:{port}')
        
        # We no longer need to add tag modification options as we've already modified the file
        cmd_parts.append(f'"{abs_file_path}"')
        
        # Join all parts with spaces
        cmd = ' '.join(cmd_parts)
        
        logging.info(f"Executing command: {cmd}")
        
        # Using shell=True to handle the complex command
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temporary file if we created one
        if temp_file:
            cleanup_temp_files(temp_file)
            
        return result
        
    except Exception as e:
        # Clean up temporary file if an exception occurred
        if temp_file:
            cleanup_temp_files(temp_file)
        raise e

def echo_dicom_using_dcm4che(host, port, ae_title):
    """
    Send DICOM echo using a simplified approach.
    
    Parameters:
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    lib_dir = get_lib_dir()
    
    # Build classpath with all necessary JARs
    classpath = os.pathsep.join([
        os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
        os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
        os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
        os.path.join(lib_dir, "logback-core-1.5.12.jar"),
        os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
        os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar") 
    ])
    
    # Simply try to associate with the server and report success if connection is established
    cmd = [
        "java", "-cp", classpath,
        "org.dcm4che3.tool.storescu.StoreSCU",
        "-b", "DICOM_SENDER", # Use a local AE title
        "-c", f"{ae_title}@{host}:{port}"
    ]
    
    logging.info(f"Executing command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # If we can connect and see "Connected to" in the output, consider it a successful echo
        if "Connected to" in result.stdout:
            result.returncode = 0  # Mark as successful
        return result
    except Exception as e:
        # Create a CompletedProcess-like object to return in case of error
        class ErrorResult:
            def __init__(self, error):
                self.returncode = 1
                self.stdout = ""
                self.stderr = str(error)
        
        return ErrorResult(e)

def send_multiple_dicom_using_dcm4che(file_paths, host, port, ae_title, progress_callback=None, dicom_tags=None):
    """
    Send multiple DICOM files using dcm4che storescu tool.
    
    Parameters:
    - file_paths: List of paths to the DICOM files
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - progress_callback: Optional callback function to update progress
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - Dictionary with results for each file
    """
    results = {}
    total_files = len(file_paths)
    
    for i, file_path in enumerate(file_paths):
        try:
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, total_files, Path(file_path).name)
                
            # Use the classpath approach for better control
            lib_dir = get_lib_dir()
            
            # Build classpath with all necessary JARs
            classpath = os.pathsep.join([
                os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
                os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
                os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
                os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
                os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
                os.path.join(lib_dir, "logback-core-1.5.12.jar"),
                os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
                # The main storescu JAR
                os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
            ])
            
            # Build the command
            cmd = [
                "java", "-cp", classpath,
                "org.dcm4che3.tool.storescu.StoreSCU",
                "-c", f"{ae_title}@{host}:{port}"
            ]
            
            # Add tag modification options if provided
            if dicom_tags and isinstance(dicom_tags, dict):
                for tag_name, tag_value in dicom_tags.items():
                    # Only add if the tag has a value
                    if tag_value:
                        # Add each argument separately to let subprocess handle escaping
                        cmd.append("-s")
                        cmd.append(f"{tag_name}={tag_value}")
            
            # We need to make sure the file path is the last argument
            # and is properly passed as a string, not split by spaces
            cmd.append("--")  # Add a separator to indicate end of options
            cmd.append(file_path)
            
            logging.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Store results
            results[file_path] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            results[file_path] = {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    # Final progress update
    if progress_callback:
        progress_callback(total_files, total_files, "Completed")
        
    return results

def send_multiple_dicom_using_dcm4che_alt(file_paths, host, port, ae_title, progress_callback=None, dicom_tags=None):
    """
    Alternative implementation for sending multiple DICOM files using shell=True.
    
    Parameters:
    - file_paths: List of paths to the DICOM files
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - progress_callback: Optional callback function to update progress
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - Dictionary with results for each file
    """
    results = {}
    total_files = len(file_paths)
    
    for i, file_path in enumerate(file_paths):
        try:
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, total_files, Path(file_path).name)
                
            # Use the alternative implementation
            result = send_dicom_using_dcm4che_alt(file_path, host, port, ae_title, dicom_tags)
            
            # Store results
            results[file_path] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            results[file_path] = {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    # Final progress update
    if progress_callback:
        progress_callback(total_files, total_files, "Completed")
        
    return results

def send_dicom_using_dcm4che_batch(file_path, host, port, ae_title, dicom_tags=None):
    """
    Implementation using a temporary batch file to ensure proper command execution.
    
    Parameters:
    - file_path: Path to the DICOM file
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - subprocess.CompletedProcess object with stdout and stderr
    """
    import tempfile
    import random
    import string
    
    # Generate a random identifier for the temp files
    random_id = ''.join(random.choice(string.ascii_letters) for _ in range(8))
    
    # Use the classpath approach for better control
    lib_dir = get_lib_dir()
    
    # Build classpath with all necessary JARs
    classpath = os.pathsep.join([
        os.path.join(lib_dir, "dcm4che-core-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-net-5.33.1.jar"),
        os.path.join(lib_dir, "dcm4che-tool-common-5.33.1.jar"),
        os.path.join(lib_dir, "commons-cli-1.9.0.jar"),
        os.path.join(lib_dir, "slf4j-api-2.0.16.jar"),
        os.path.join(lib_dir, "logback-core-1.5.12.jar"),
        os.path.join(lib_dir, "logback-classic-1.5.12.jar"),
        os.path.join(lib_dir, "dcm4che-tool-storescu-5.33.1.jar")
    ])
    
    # Create a temporary batch file
    with tempfile.NamedTemporaryFile(suffix=".bat", delete=False, mode='w') as batch_file:
        batch_file_path = batch_file.name
        
        # Write the command to the batch file
        batch_file.write(f'@echo off\n')
        batch_file.write(f'java -cp "{classpath}" org.dcm4che3.tool.storescu.StoreSCU -c {ae_title}@{host}:{port}')
        
        # Add tag modification options if provided
        if dicom_tags and isinstance(dicom_tags, dict):
            for tag_name, tag_value in dicom_tags.items():
                if tag_value:
                    if ' ' in tag_value:
                        batch_file.write(f' -s {tag_name}="{tag_value}"')
                    else:
                        batch_file.write(f' -s {tag_name}={tag_value}')
        
        # Create a copy of the file with a standard name
        temp_dir = tempfile.gettempdir()
        dicom_temp_filename = f"dicom_{random_id}.dcm"
        dicom_temp_path = os.path.join(temp_dir, dicom_temp_filename)
        
        # Copy the DICOM file to the temporary location
        import shutil
        shutil.copy2(file_path, dicom_temp_path)
        
        # Add the file path to the batch command
        batch_file.write(f' "{dicom_temp_path}"\n')
        
        # Add output redirection
        output_file_path = os.path.join(temp_dir, f"output_{random_id}.txt")
        error_file_path = os.path.join(temp_dir, f"error_{random_id}.txt")
        batch_file.write(f'> "{output_file_path}" 2> "{error_file_path}"\n')
    
    # Execute the batch file
    logging.info(f"Executing batch file: {batch_file_path}")
    process = subprocess.run(batch_file_path, shell=True, capture_output=True, text=True)
    
    # Read the output and error files
    try:
        with open(output_file_path, 'r') as f:
            stdout = f.read()
        with open(error_file_path, 'r') as f:
            stderr = f.read()
    except Exception as e:
        stdout = f"Failed to read output: {str(e)}"
        stderr = f"Failed to read error: {str(e)}"
    
    # Create a result object similar to what subprocess.run would return
    class BatchResult:
        def __init__(self, returncode, stdout, stderr):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr
    
    # Determine return code based on stderr content
    return_code = 0 if not stderr.strip() else 1
    result = BatchResult(return_code, stdout, stderr)
    
    # Clean up temporary files
    try:
        os.remove(batch_file_path)
        os.remove(dicom_temp_path)
        os.remove(output_file_path)
        os.remove(error_file_path)
        logging.info("Cleaned up temporary files")
    except Exception as e:
        logging.warning(f"Failed to clean up temporary files: {str(e)}")
    
    return result

def send_multiple_dicom_using_dcm4che_batch(file_paths, host, port, ae_title, progress_callback=None, dicom_tags=None):
    """
    Implementation for sending multiple DICOM files using the batch file approach.
    
    Parameters:
    - file_paths: List of paths to the DICOM files
    - host: PACS server hostname/IP
    - port: PACS server port
    - ae_title: AE Title of the PACS server
    - progress_callback: Optional callback function to update progress
    - dicom_tags: Dictionary of DICOM tags to modify (e.g., {"PatientID": "12345", "PatientName": "ANONYMOUS"})
    
    Returns:
    - Dictionary with results for each file
    """
    results = {}
    total_files = len(file_paths)
    
    for i, file_path in enumerate(file_paths):
        try:
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, total_files, Path(file_path).name)
                
            # Use the batch file approach
            result = send_dicom_using_dcm4che_batch(file_path, host, port, ae_title, dicom_tags)
            
            # Store results
            results[file_path] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            results[file_path] = {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    # Final progress update
    if progress_callback:
        progress_callback(total_files, total_files, "Completed")
        
    return results 