import 'dart:io';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:logger/logger.dart';

class ResumeFileService {
  static const String resumesFolderName = 'resumes';
  static final logger = Logger();

  /// Ensure the resumes folder exists, creating it if necessary
  static Future<Directory> ensureResumesFolderExists() async {
    try {
      final String folderPath = await getResumesFolderPath();
      final Directory resumesDir = Directory(folderPath);

      if (!await resumesDir.exists()) {
        await resumesDir.create(recursive: true);
        logger.i('✓ Created resumes folder: $folderPath');
      } else {
        logger.i('✓ Resumes folder exists: $folderPath');
      }

      return resumesDir;
    } catch (e) {
      logger.e('Error ensuring resumes folder exists: $e');
      rethrow;
    }
  }

  /// Get the resumes folder path in user's documents directory
  /// Returns: C:\Users\<User>\Documents\BT-Resume\resumes on Windows
  ///          ~/Documents/BT-Resume/resumes on macOS/Linux
  static Future<String> getResumesFolderPath() async {
    try {
      final Directory documentDir = await getApplicationDocumentsDirectory();
      final String appDataPath = p.join(documentDir.path, 'BT-Resume');
      return p.join(appDataPath, resumesFolderName);
    } catch (e) {
      logger.e('Error getting resumes folder path: $e');
      // Fallback to current directory if path_provider fails
      return p.join(Directory.current.path, resumesFolderName);
    }
  }

  /// Get the outputs folder path in user's documents directory
  /// Returns: C:\Users\<User>\Documents\BT-Resume\outputs on Windows
  ///          ~/Documents/BT-Resume/outputs on macOS/Linux
  static Future<String> getOutputsFolderPath() async {
    try {
      final Directory documentDir = await getApplicationDocumentsDirectory();
      final String appDataPath = p.join(documentDir.path, 'BT-Resume');
      return p.join(appDataPath, 'outputs');
    } catch (e) {
      logger.e('Error getting outputs folder path: $e');
      // Fallback to current directory if path_provider fails
      return p.join(Directory.current.path, 'outputs');
    }
  }

  /// List all PDF files in the resumes folder (Documents/BT-Resume/resumes)
  static Future<List<File>> listResumeFiles() async {
    try {
      // Ensure the folder exists first
      final Directory resumesDir = await ensureResumesFolderExists();

      final List<FileSystemEntity> files = resumesDir.listSync();
      final List<File> pdfFiles = files
          .whereType<File>()
          .where((file) => file.path.toLowerCase().endsWith('.pdf'))
          .toList();

      // Sort by modification time (newest first)
      pdfFiles.sort((a, b) => b.lastModifiedSync().compareTo(a.lastModifiedSync()));

      logger.i('✓ Found ${pdfFiles.length} resume(s) in ${resumesDir.path}');
      return pdfFiles;
    } catch (e) {
      logger.e('Error listing resume files: $e');
      return [];
    }
  }

  /// Get the file name from a file path
  static String getFileName(String filePath) {
    return p.basename(filePath);
  }

  /// Get the file modification date
  static String getLastModified(File file) {
    try {
      final DateTime modified = file.lastModifiedSync();
      final Duration diff = DateTime.now().difference(modified);

      if (diff.inDays == 0) {
        return 'Updated today';
      } else if (diff.inDays == 1) {
        return 'Updated yesterday';
      } else if (diff.inDays < 7) {
        return 'Updated ${diff.inDays} days ago';
      } else if (diff.inDays < 30) {
        final weeks = (diff.inDays / 7).floor();
        return 'Updated $weeks week(s) ago';
      } else {
        final months = (diff.inDays / 30).floor();
        return 'Updated $months month(s) ago';
      }
    } catch (e) {
      return 'Unknown date';
    }
  }

  /// Download a resume PDF to the user's Downloads folder
  static Future<String?> downloadResume(
    File sourceFile,
    String newFileName, {
    bool replaceOriginal = false,
    String? customDownloadPath,
  }) async {
    try {
      String destinationPath;

      if (replaceOriginal) {
        // Replace original - save to same location as source
        final sourceDir = sourceFile.parent;
        destinationPath = sourceDir.path;
      } else if (customDownloadPath != null) {
        // Use custom path if provided
        destinationPath = customDownloadPath;
      } else {
        // Default: Download to resumes folder (same place we read from)
        destinationPath = await getResumesFolderPath();
      }

      // Ensure filename ends with .pdf
      final fileName =
          newFileName.endsWith('.pdf') ? newFileName : '$newFileName.pdf';

      // Create destination file path
      final fullDestinationPath = p.join(destinationPath, fileName);
      final destinationFile = File(fullDestinationPath);

      // Copy the file
      await sourceFile.copy(fullDestinationPath);

      if (replaceOriginal) {
        logger.i('✓ Resume replaced: $fileName');
      } else {
        logger.i('✓ Downloaded resume: $fileName to $destinationPath');
      }

      return fullDestinationPath;
    } catch (e) {
      logger.e('Error downloading resume: $e');
      return null;
    }
  }

  /// Delete a resume file
  /// Returns: true if successful, false otherwise
  static Future<bool> deleteResume(String filePath) async {
    try {
      final file = File(filePath);
      if (await file.exists()) {
        await file.delete();
        logger.i('✓ Deleted resume: $filePath');
        return true;
      } else {
        logger.w('Resume file not found: $filePath');
        return false;
      }
    } catch (e) {
      logger.e('Error deleting resume: $e');
      return false;
    }
  }
}
