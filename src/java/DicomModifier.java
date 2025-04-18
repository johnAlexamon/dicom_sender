import org.dcm4che3.data.Attributes;
import org.dcm4che3.data.Tag;
import org.dcm4che3.data.VR;
import org.dcm4che3.io.DicomInputStream;
import org.dcm4che3.io.DicomOutputStream;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * A utility class to modify DICOM attributes using dcm4che3 library
 */
public class DicomModifier {

    /**
     * Modifies DICOM tags in a file and saves to a new file
     * 
     * @param inputPath  Path to the input DICOM file
     * @param outputPath Path where the modified DICOM file will be saved
     * @param tagModifications Map of tag to value modifications (format: "00100010=NEWNAME")
     * @return true if successful, false otherwise
     */
    public static boolean modifyDicom(String inputPath, String outputPath, String[] tagModifications) {
        try {
            // Read the DICOM file
            DicomInputStream dis = new DicomInputStream(new File(inputPath));
            Attributes attributes = dis.readDataset();
            
            // Store original file meta information
            Attributes fileMetaInfo = dis.getFileMetaInformation();
            dis.close();
            
            // Apply tag modifications
            for (String modification : tagModifications) {
                String[] parts = modification.split("=", 2);
                if (parts.length == 2) {
                    String tagStr = parts[0];
                    String value = parts[1];
                    
                    // Parse tag to integer value (assuming format like 00100010)
                    int tag = Integer.parseInt(tagStr, 16);
                    
                    // Get VR for the tag from the existing attributes if possible
                    VR vr = attributes.getVR(tag);
                    if (vr == null) {
                        // Handle special cases for different types of tags
                        if (tag == Tag.PatientName) {
                            vr = VR.PN;  // Person Name
                        } else if (tag == Tag.StudyInstanceUID || tag == Tag.SeriesInstanceUID || 
                                  tag == Tag.SOPInstanceUID || tagStr.endsWith("UID")) {
                            vr = VR.UI;  // UID type
                        } else {
                            vr = VR.LO;  // Default to Long String
                        }
                    }
                    
                    // Set the new value
                    attributes.setString(tag, vr, value);
                    System.out.println("Modified tag " + tagStr + " to: " + value);
                }
            }
            
            // Write the modified dataset to the output file
            DicomOutputStream dos = new DicomOutputStream(new File(outputPath));
            dos.writeDataset(fileMetaInfo, attributes);
            dos.close();
            
            System.out.println("DICOM file successfully modified and saved to: " + outputPath);
            return true;
            
        } catch (Exception e) {
            System.err.println("Error modifying DICOM file: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * Main method to run the DICOM modifier from command line
     */
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java DicomModifier <input-file> <output-file> [tag=value] [tag=value] ...");
            System.exit(1);
        }
        
        String inputFile = args[0];
        String outputFile = args[1];
        
        // Collect tag modifications from remaining arguments
        String[] modifications = new String[args.length - 2];
        System.arraycopy(args, 2, modifications, 0, args.length - 2);
        
        boolean success = modifyDicom(inputFile, outputFile, modifications);
        System.exit(success ? 0 : 1);
    }
} 