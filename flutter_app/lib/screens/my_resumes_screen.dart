import 'package:flutter/material.dart';
import 'dart:io';
import 'package:url_launcher/url_launcher.dart';
import 'package:file_picker/file_picker.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../services/resume_file_service.dart';

class MyResumesScreen extends StatefulWidget {
  const MyResumesScreen({Key? key}) : super(key: key);

  @override
  State<MyResumesScreen> createState() => _MyResumesScreenState();
}

class _MyResumesScreenState extends State<MyResumesScreen> {
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isAddingResume = false;

  @override
  void initState() {
    super.initState();
    _loadResumeFiles();
  }

  Future<void> _loadResumeFiles() async {
    try {
      final files = await ResumeFileService.listResumeFiles();
      setState(() {
        resumeFiles = files;
        isLoading = false;
      });
    } catch (e) {
      print('Error loading resumes: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> _addResume() async {
    try {
      setState(() {
        isAddingResume = true;
      });

      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final pickedFile = result.files.first;
        final sourceFile = File(pickedFile.path!);

        // Get destination folder
        final resumesFolderPath = ResumeFileService.getResumesFolderPath();
        final resumesDir = Directory(resumesFolderPath);

        // Create folder if it doesn't exist
        if (!await resumesDir.exists()) {
          await resumesDir.create(recursive: true);
        }

        // Copy file to resumes folder
        final destFile = File('${resumesFolderPath}/${pickedFile.name}');
        await sourceFile.copy(destFile.path);

        // Reload the list
        await _loadResumeFiles();

        // Show success message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Resume added: ${pickedFile.name}'),
              backgroundColor: AppColors.successGreen,
            ),
          );
        }
      }
    } catch (e) {
      print('Error adding resume: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Error adding resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    } finally {
      setState(() {
        isAddingResume = false;
      });
    }
  }

  Future<void> _openResume(File file) async {
    try {
      final Uri uri = Uri.file(file.path);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Could not open resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    } catch (e) {
      print('Error opening resume: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Error opening resume'),
          backgroundColor: AppColors.errorRed,
        ),
      );
    }
  }

  String _getFileSizeText(File file) {
    try {
      final bytes = file.lengthSync();
      if (bytes < 1024) {
        return '${bytes}B';
      } else if (bytes < 1024 * 1024) {
        return '${(bytes / 1024).toStringAsFixed(1)}KB';
      } else {
        return '${(bytes / (1024 * 1024)).toStringAsFixed(1)}MB';
      }
    } catch (e) {
      return 'Unknown';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Left Panel - Resume List & Grading (40%)
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Resume List with Header
                Expanded(
                  flex: 50,
                  child: Container(
                    margin: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: AppColors.gold.withOpacity(0.3),
                        width: 1,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        // Header inside border
                        Padding(
                          padding: const EdgeInsets.all(5.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(
                                'My Resumes',
                                textAlign: TextAlign.center,
                                style: AppTypography.labelText.copyWith(
                                  color: AppColors.cream,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${resumeFiles.length} resume(s)',
                                textAlign: TextAlign.center,
                                style: AppTypography.bodySmall.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                        // Divider under header
                        Container(
                          height: 1,
                          color: AppColors.gold.withOpacity(0.3),
                        ),
                        // Content
                        Expanded(
                          child: isLoading
                              ? Center(
                                  child: Column(
                                    mainAxisAlignment:
                                        MainAxisAlignment.center,
                                    children: [
                                      const CircularProgressIndicator(
                                        valueColor:
                                            AlwaysStoppedAnimation<Color>(
                                                AppColors.gold),
                                      ),
                                      const SizedBox(height: 16),
                                      Text(
                                        'Loading resumes...',
                                        style: AppTypography.bodySmall
                                            .copyWith(
                                          color: AppColors.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ),
                                )
                              : resumeFiles.isEmpty
                                  ? Center(
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.description_outlined,
                                            size: 48,
                                            color: AppColors.textSecondary,
                                          ),
                                          const SizedBox(height: 16),
                                          Text(
                                            'No resumes found',
                                            style: AppTypography.bodyLarge
                                                .copyWith(
                                              color: AppColors.textSecondary,
                                            ),
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            'Place PDFs in the resumes folder',
                                            style: AppTypography.bodySmall
                                                .copyWith(
                                              color: AppColors.textTertiary,
                                            ),
                                          ),
                                        ],
                                      ),
                                    )
                                  : Column(
                                      children: [
                                        Expanded(
                                          child: ListView.builder(
                                            padding: const EdgeInsets
                                                .symmetric(
                                                horizontal: 12),
                                            itemCount: resumeFiles.length,
                                            itemBuilder: (context, index) {
                                              final isSelected =
                                                  selectedResumeIndex ==
                                                      index;
                                              final fileName =
                                                  ResumeFileService
                                                      .getFileName(
                                                  resumeFiles[index].path);
                                              final lastModified =
                                                  ResumeFileService
                                                      .getLastModified(
                                                  resumeFiles[index]);
                                              final fileSize =
                                                  _getFileSizeText(
                                                  resumeFiles[index]);

                                              return GestureDetector(
                                                onTap: () {
                                                  setState(() {
                                                    selectedResumeIndex =
                                                        index;
                                                  });
                                                },
                                                child: Container(
                                                  margin: const EdgeInsets
                                                      .only(bottom: 12),
                                                  padding:
                                                      const EdgeInsets
                                                          .all(12),
                                                  decoration:
                                                      BoxDecoration(
                                                    color: isSelected
                                                        ? AppColors.dark3
                                                        : AppColors.dark2,
                                                    borderRadius:
                                                        BorderRadius
                                                            .circular(8),
                                                    border: Border.all(
                                                      color: isSelected
                                                          ? AppColors.gold
                                                          : AppColors
                                                              .dark3,
                                                      width: isSelected
                                                          ? 2
                                                          : 1,
                                                    ),
                                                  ),
                                                  child: Column(
                                                    crossAxisAlignment:
                                                        CrossAxisAlignment
                                                            .start,
                                                    children: [
                                                      Row(
                                                        children: [
                                                          Icon(
                                                            Icons
                                                                .picture_as_pdf,
                                                            color: AppColors
                                                                .errorRed,
                                                            size: 18,
                                                          ),
                                                          const SizedBox(
                                                              width: 8),
                                                          Expanded(
                                                            child: Text(
                                                              fileName,
                                                              style: AppTypography
                                                                  .labelText
                                                                  .copyWith(
                                                                color: AppColors
                                                                    .cream,
                                                                fontSize: 12,
                                                              ),
                                                              overflow:
                                                                  TextOverflow
                                                                      .ellipsis,
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                      const SizedBox(
                                                          height: 4),
                                                      Row(
                                                        mainAxisAlignment:
                                                            MainAxisAlignment
                                                                .spaceBetween,
                                                        children: [
                                                          Text(
                                                            lastModified,
                                                            style: AppTypography
                                                                .bodySmall
                                                                .copyWith(
                                                              color: AppColors
                                                                  .textSecondary,
                                                              fontSize: 10,
                                                            ),
                                                          ),
                                                          Text(
                                                            fileSize,
                                                            style: AppTypography
                                                                .bodySmall
                                                                .copyWith(
                                                              color: AppColors
                                                                  .textTertiary,
                                                              fontSize: 9,
                                                            ),
                                                          ),
                                                        ],
                                                      ),
                                                    ],
                                                  ),
                                                ),
                                              );
                                            },
                                          ),
                                        ),
                                        Padding(
                                          padding:
                                              const EdgeInsets.all(12.0),
                                          child: SizedBox(
                                            width: double.infinity,
                                            child: ElevatedButton.icon(
                                              onPressed: isAddingResume
                                                  ? null
                                                  : _addResume,
                                              icon: isAddingResume
                                                  ? SizedBox(
                                                      width: 18,
                                                      height: 18,
                                                      child:
                                                          CircularProgressIndicator(
                                                        valueColor:
                                                            AlwaysStoppedAnimation<
                                                                Color>(
                                                          isAddingResume
                                                              ? AppColors
                                                                  .darkPrimary
                                                              : AppColors
                                                                  .darkPrimary,
                                                        ),
                                                        strokeWidth: 2,
                                                      ),
                                                    )
                                                  : const Icon(Icons.add),
                                              label: Text(
                                                isAddingResume
                                                    ? 'Adding...'
                                                    : 'Add Resume',
                                              ),
                                              style: ElevatedButton
                                                  .styleFrom(
                                                backgroundColor:
                                                    AppColors.gold,
                                                foregroundColor: AppColors
                                                    .darkPrimary,
                                                padding: const EdgeInsets
                                                    .symmetric(
                                                    vertical: 12),
                                                disabledBackgroundColor:
                                                    AppColors.dark3,
                                                disabledForegroundColor:
                                                    AppColors
                                                        .textSecondary,
                                              ),
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Divider
                Container(
                  height: 1,
                  color: AppColors.dark3,
                ),

                // Grade Resume Section
                Expanded(
                  flex: 50,
                  child: Container(
                    margin: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: AppColors.gold.withOpacity(0.3),
                        width: 1,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        // Header inside border
                        Padding(
                          padding: const EdgeInsets.all(.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(
                                'Resume Grade',
                                textAlign: TextAlign.center,
                                style: AppTypography.labelText.copyWith(
                                  color: AppColors.cream,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        // Divider under header
                        Container(
                          height: 1,
                          color: AppColors.gold.withOpacity(0.3),
                        ),
                        // Content
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                        // Grade Score
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppColors.dark2,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppColors.dark3),
                          ),
                          child: Column(
                            children: [
                              Text(
                                'Current Score',
                                style: AppTypography.bodySmall.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                '7.8/10',
                                style: AppTypography.headingPageTitle.copyWith(
                                  color: AppColors.gold,
                                  fontSize: 28,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Good - Ready to Apply',
                                style: AppTypography.bodySmall.copyWith(
                                  color: AppColors.successGreen,
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Grade Button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: () {
                              // TODO: Grade resume
                            },
                            icon: const Icon(Icons.assessment),
                            label: const Text('Get Fresh Grade'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.gold,
                              foregroundColor: AppColors.darkPrimary,
                              padding:
                                  const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                        ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        // Divider
        Container(
          width: 1,
          color: AppColors.dark3,
        ),

        // Right Panel - Resume Preview (60%)
        Expanded(
          flex: 60,
          child: Container(
            color: AppColors.darkPrimary,
            child: resumeFiles.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.description_outlined,
                          size: 64,
                          color: AppColors.textSecondary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'No Resume Selected',
                          style: AppTypography.headingPageTitle.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Select a resume from the list to preview',
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  )
                : Column(
                    children: [
                      // Preview Header
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(color: AppColors.dark3),
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment:
                              MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Resume Preview',
                                  style: AppTypography.labelText.copyWith(
                                    color: AppColors.cream,
                                    fontSize: 14,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  ResumeFileService.getFileName(
                                      resumeFiles[selectedResumeIndex].path),
                                  style: AppTypography.bodySmall.copyWith(
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                              ],
                            ),
                            Row(
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.open_in_new),
                                  color: AppColors.gold,
                                  tooltip: 'Open with system viewer',
                                  onPressed: () {
                                    _openResume(
                                        resumeFiles[selectedResumeIndex]);
                                  },
                                ),
                                IconButton(
                                  icon: const Icon(Icons.download),
                                  color: AppColors.gold,
                                  tooltip: 'Download',
                                  onPressed: () {
                                    // TODO: Download resume
                                  },
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      // Preview Content - PDF Viewer
                      Expanded(
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppColors.dark3),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: SfPdfViewer.file(
                              resumeFiles[selectedResumeIndex],
                              pageLayoutMode: PdfPageLayoutMode.continuous,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }
}