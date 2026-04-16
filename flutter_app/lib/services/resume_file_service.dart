import 'dart:io';
import 'package:path/path.dart' as p;

class ResumeFileService {
  static const String resumesFolderName = 'resumes';

  /// Get the resumes folder path relative to the project root
  static String getResumesFolderPath() {
    // Get the current working directory and navigate to resumes folder
    final String projectRoot = Directory.current.path;
    return p.join(projectRoot, resumesFolderName);
  }

  /// List all PDF files in the resumes folder
  static Future<List<File>> listResumeFiles() async {
    try {
      final String folderPath = getResumesFolderPath();
      final Directory resumesDir = Directory(folderPath);

      if (!await resumesDir.exists()) {
        return [];
      }

      final List<FileSystemEntity> files = resumesDir.listSync();
      final List<File> pdfFiles = files
          .whereType<File>()
          .where((file) => file.path.toLowerCase().endsWith('.pdf'))
          .toList();

      // Sort by name
      pdfFiles.sort((a, b) => a.path.compareTo(b.path));

      return pdfFiles;
    } catch (e) {
      print('Error listing resume files: $e');
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
}
