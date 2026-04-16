import 'package:flutter/material.dart';
import 'dart:io';
import 'package:url_launcher/url_launcher.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../services/resume_file_service.dart';

class PolishChange {
  final String icon;
  final String title;
  final String description;

  PolishChange({
    required this.icon,
    required this.title,
    required this.description,
  });
}

class PolishScreen extends StatefulWidget {
  const PolishScreen({Key? key}) : super(key: key);

  @override
  State<PolishScreen> createState() => _PolishScreenState();
}

class _PolishScreenState extends State<PolishScreen> {
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isPolishing = false;
  bool hasPolished = false;
  List<PolishChange> polishChanges = [];

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

  Future<void> _polishResume() async {
    try {
      setState(() {
        isPolishing = true;
      });

      // TODO: Call backend API to polish resume
      // For now, simulate the process with mock data
      await Future.delayed(const Duration(seconds: 2));

      setState(() {
        hasPolished = true;
        isPolishing = false;
        polishChanges = [
          PolishChange(
            icon: '✓',
            title: '4 bullets enhanced',
            description: 'Strengthened action verbs and impact metrics',
          ),
          PolishChange(
            icon: '✓',
            title: 'Keywords optimized',
            description: 'Added 8 industry-relevant keywords',
          ),
          PolishChange(
            icon: '✓',
            title: 'Formatting improved',
            description: 'Better spacing and readability',
          ),
        ];
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Resume polish complete!'),
            backgroundColor: AppColors.successGreen,
          ),
        );
      }
    } catch (e) {
      print('Error polishing resume: $e');
      setState(() {
        isPolishing = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Error polishing resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  void _resetPolish() {
    setState(() {
      hasPolished = false;
      polishChanges = [];
    });
  }

  Future<void> _openResume(File file) async {
    try {
      final Uri uri = Uri.file(file.path);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
    } catch (e) {
      print('Error opening resume: $e');
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
        // Left Panel - Resume List (40%)
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Resume List Section (with Header)
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
                                'Select Resume to Polish',
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
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const CircularProgressIndicator(
                                      valueColor: AlwaysStoppedAnimation<Color>(
                                          AppColors.gold),
                                    ),
                                    const SizedBox(height: 16),
                                    Text(
                                      'Loading resumes...',
                                      style: AppTypography.bodySmall.copyWith(
                                        color: AppColors.textSecondary,
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            : resumeFiles.isEmpty
                                ? Center(
                                    child: Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        Icon(
                                          Icons.description_outlined,
                                          size: 48,
                                          color: AppColors.textSecondary,
                                        ),
                                        const SizedBox(height: 16),
                                        Text(
                                          'No resumes found',
                                          style: AppTypography.bodyLarge.copyWith(
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          'Add a resume first',
                                          style: AppTypography.bodySmall.copyWith(
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
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 12, vertical: 8),
                                          itemCount: resumeFiles.length,
                                          itemBuilder: (context, index) {
                                            final isSelected =
                                                selectedResumeIndex == index;
                                            final fileName =
                                                ResumeFileService.getFileName(
                                                    resumeFiles[index].path);
                                            final lastModified =
                                                ResumeFileService.getLastModified(
                                                    resumeFiles[index]);
                                            final fileSize =
                                                _getFileSizeText(
                                                    resumeFiles[index]);

                                            return GestureDetector(
                                              onTap: () {
                                                setState(() {
                                                  selectedResumeIndex = index;
                                                  _resetPolish();
                                                });
                                              },
                                              child: Container(
                                                margin: const EdgeInsets.only(
                                                  bottom: 12,
                                                ),
                                                padding:
                                                    const EdgeInsets.all(12),
                                                decoration: BoxDecoration(
                                                  color: isSelected
                                                      ? AppColors.dark3
                                                      : AppColors.dark2,
                                                  borderRadius:
                                                      BorderRadius.circular(8),
                                                  border: Border.all(
                                                    color: isSelected
                                                        ? AppColors.gold
                                                        : AppColors.dark3,
                                                    width: isSelected ? 2 : 1,
                                                  ),
                                                ),
                                                child: Column(
                                                  crossAxisAlignment:
                                                      CrossAxisAlignment.start,
                                                  children: [
                                                    Row(
                                                      children: [
                                                        Icon(
                                                          Icons.picture_as_pdf,
                                                          color: AppColors
                                                              .errorRed,
                                                          size: 18,
                                                        ),
                                                        const SizedBox(
                                                          width: 8,
                                                        ),
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
                                                      height: 4,
                                                    ),
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
                              ],
                            ),
                          ),
                        ),
                      ],
              ],
                    ),
                  ),
                ),

                // Divider
                Container(
                  height: 1,
                  color: AppColors.dark3,
                ),

                // Polish Section
                Expanded(
                  flex: 50,
                  child: Container(
                    padding: const EdgeInsets.all(16.0),
                    child: hasPolished
                        ? Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    Icons.check_circle,
                                    color: AppColors.successGreen,
                                    size: 20,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Changes Applied',
                                    style: AppTypography.labelText.copyWith(
                                      color: AppColors.cream,
                                      fontSize: 13,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Expanded(
                                child: ListView.builder(
                                  itemCount: polishChanges.length,
                                  itemBuilder: (context, index) {
                                    final change = polishChanges[index];
                                    return Container(
                                      margin:
                                          const EdgeInsets.only(bottom: 10),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 10,
                                        vertical: 8,
                                      ),
                                      decoration: BoxDecoration(
                                        color: AppColors.darkPrimary,
                                        borderRadius:
                                            BorderRadius.circular(6),
                                        border: Border.all(
                                          color: AppColors.dark3,
                                        ),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              Text(
                                                change.icon,
                                                style: AppTypography.bodyLarge
                                                    .copyWith(
                                                  color: AppColors
                                                      .successGreen,
                                                  fontSize: 14,
                                                ),
                                              ),
                                              const SizedBox(width: 8),
                                              Expanded(
                                                child: Text(
                                                  change.title,
                                                  style: AppTypography
                                                      .labelText
                                                      .copyWith(
                                                    color: AppColors.cream,
                                                    fontSize: 12,
                                                  ),
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            change.description,
                                            style: AppTypography.bodySmall
                                                .copyWith(
                                              color: AppColors.textSecondary,
                                              fontSize: 10,
                                            ),
                                          ),
                                        ],
                                      ),
                                    );
                  },
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _resetPolish,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.dark3,
                        foregroundColor: AppColors.cream,
                        padding: const EdgeInsets.symmetric(
                          vertical: 10,
                        ),
                      ),
                      child: const Text(
                        'Try Again',
                        style: TextStyle(fontSize: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          )
          : Center(
            child: Text(
              'Polish your resume to see changes here',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ),
      // Vertical Divider
      Container(
          width: 1,
          color: AppColors.dark3,
        ),

        // Right Panel - Preview & Polish (60%)
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
                          Icons.auto_awesome,
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
                          'Select a resume from the list to polish',
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  )
                : Column(
                    children: [
                      // Header
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
                            if (!hasPolished)
                              IconButton(
                                icon: const Icon(Icons.download),
                                color: AppColors.textTertiary,
                                tooltip: 'Polish resume to download',
                                onPressed: null,
                              )
                            else
                              IconButton(
                                icon: const Icon(Icons.download),
                                color: AppColors.gold,
                                tooltip: 'Download polished resume',
                                onPressed: () {
                                  // TODO: Download polished resume
                                },
                              ),
                          ],
                        ),
                      ),

                      // Preview & Changes Content
                      Expanded(
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppColors.dark3),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Stack(
                              children: [
                                SfPdfViewer.file(
                                  resumeFiles[selectedResumeIndex],
                                  pageLayoutMode:
                                      PdfPageLayoutMode.continuous,
                                ),
                                if (isPolishing)
                                  Container(
                                    color: AppColors.darkPrimary
                                        .withOpacity(0.7),
                                    child: Center(
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          const CircularProgressIndicator(
                                            valueColor:
                                                AlwaysStoppedAnimation<Color>(
                                              AppColors.gold,
                                            ),
                                          ),
                                          const SizedBox(height: 16),
                                          Text(
                                            'Polishing resume...',
                                            style: AppTypography.bodySmall
                                                .copyWith(
                                              color: AppColors.cream,
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
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }
}