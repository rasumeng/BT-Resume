import 'package:flutter/material.dart';
import 'dart:io';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../services/resume_file_service.dart';

class TailorMatch {
  final String category;
  final String keyword;
  final String relevance;

  TailorMatch({
    required this.category,
    required this.keyword,
    required this.relevance,
  });
}

class TailorScreen extends StatefulWidget {
  const TailorScreen({Key? key}) : super(key: key);

  @override
  State<TailorScreen> createState() => _TailorScreenState();
}

class _TailorScreenState extends State<TailorScreen> {
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isTailoring = false;
  bool hasTailored = false;
  List<TailorMatch> tailorMatches = [];
  
  final TextEditingController jobPositionController = TextEditingController();
  final TextEditingController jobCompanyController = TextEditingController();
  final TextEditingController jobDescriptionController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadResumeFiles();
  }

  @override
  void dispose() {
    jobPositionController.dispose();
    jobCompanyController.dispose();
    jobDescriptionController.dispose();
    super.dispose();
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

  Future<void> _tailorResume() async {
    if (jobDescriptionController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Please enter a job description'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    try {
      setState(() {
        isTailoring = true;
      });

      // TODO: Call backend API to tailor resume
      // Include: resume file, job position (optional), company (optional), job description
      // For now, simulate the process with mock data
      await Future.delayed(const Duration(seconds: 2));

      setState(() {
        hasTailored = true;
        isTailoring = false;
        tailorMatches = [
          TailorMatch(
            category: 'Skills Match',
            keyword: 'Project Management',
            relevance: '92%',
          ),
          TailorMatch(
            category: 'Skills Match',
            keyword: 'Agile/Scrum',
            relevance: '88%',
          ),
          TailorMatch(
            category: 'Experience Match',
            keyword: 'Cross-functional team leadership',
            relevance: '95%',
          ),
          TailorMatch(
            category: 'Experience Match',
            keyword: 'Budget management (5-7 years)',
            relevance: '87%',
          ),
          TailorMatch(
            category: 'Keyword Matches',
            keyword: 'Data-driven decision making',
            relevance: '91%',
          ),
          TailorMatch(
            category: 'Keyword Matches',
            keyword: 'Stakeholder communication',
            relevance: '85%',
          ),
        ];
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Resume tailored successfully!'),
            backgroundColor: AppColors.successGreen,
          ),
        );
      }
    } catch (e) {
      print('Error tailoring resume: $e');
      setState(() {
        isTailoring = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Error tailoring resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  void _resetTailor() {
    setState(() {
      hasTailored = false;
      tailorMatches = [];
    });
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
        // Left Panel - Inputs & Results (40%)
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: isLoading
                ? Center(
                    child: CircularProgressIndicator(
                      color: AppColors.gold,
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
                          // Resume List Section
                          Expanded(
                            flex: 45,
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
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Padding(
                                    padding: const EdgeInsets.all(5.0),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.center,
                                      children: [
                                        Text(
                                          'Select Resume',
                                          textAlign: TextAlign.center,
                                          style: AppTypography.labelText
                                              .copyWith(
                                            color: AppColors.cream,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          '${resumeFiles.length} resume${resumeFiles.length != 1 ? 's' : ''}',
                                          textAlign: TextAlign.center,
                                          style: AppTypography.bodySmall
                                              .copyWith(
                                          color: AppColors.textSecondary,
                                          fontSize: 11,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                // Divider
                                Container(
                                  height: 1,
                                  color: AppColors.dark2,
                                ),
                                Expanded(
                                  child: ListView.builder(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 12, vertical: 8),
                                    itemCount: resumeFiles.length,
                                    itemBuilder: (context, index) {
                                      final file = resumeFiles[index];
                                      final isSelected =
                                          selectedResumeIndex == index;
                                      final fileName =
                                          ResumeFileService.getFileName(
                                              file.path);
                                      final lastModified =
                                          ResumeFileService.getLastModified(
                                              file);
                                      final fileSize =
                                          _getFileSizeText(file);

                                      return GestureDetector(
                                        onTap: () {
                                          setState(() {
                                            selectedResumeIndex = index;
                                          });
                                        },
                                        child: Container(
                                          margin: const EdgeInsets.only(
                                              bottom: 12),
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
                                                    color:
                                                        AppColors.errorRed,
                                                    size: 18,
                                                  ),
                                                  const SizedBox(width: 8),
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
                                              const SizedBox(height: 4),
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

                          // Divider
                          Container(
                            height: 1,
                            color: AppColors.dark3,
                          ),

                          // Job Details & Results Section
                          Expanded(
                            flex: 55,
                            child: Container(
                              margin: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: AppColors.gold.withOpacity(0.3),
                                  width: 1,
                                ),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: SingleChildScrollView(
                                child: Padding(
                                  padding: const EdgeInsets.all(16.0),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      // Header
                                      Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.center,
                                        children: [
                                        Text(
                                          'Job Details',
                                          textAlign: TextAlign.center,
                                          style: AppTypography.labelText.copyWith(
                                            color: AppColors.cream,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          'Enter job information to tailor your resume',
                                          textAlign: TextAlign.center,
                                          style: AppTypography.bodySmall.copyWith(
                                            color: AppColors.textSecondary,
                                            fontSize: 11,
                                          ),
                                        ),
                                      ],
                                    ),
                                    // Divider
                                    Container(
                                      height: 1,
                                      color: AppColors.dark2,
                                      margin: const EdgeInsets.symmetric(vertical: 16),
                                    ),
                                    const SizedBox(height: 0),
                                    // Position Title Input
                                    TextField(
                                      controller: jobPositionController,
                                      style: AppTypography.bodySmall.copyWith(
                                        color: AppColors.cream,
                                      ),
                                      decoration: InputDecoration(
                                        labelText: 'Job Position (Optional)',
                                        labelStyle:
                                            AppTypography.bodySmall.copyWith(
                                          color: AppColors.textSecondary,
                                          fontSize: 12,
                                        ),
                                        hintText:
                                            'e.g. Senior Product Manager',
                                        hintStyle:
                                            AppTypography.bodySmall.copyWith(
                                          color: AppColors.textSecondary,
                                          fontSize: 11,
                                        ),
                                        border: OutlineInputBorder(
                                          borderRadius:
                                              BorderRadius.circular(6),
                                          borderSide: BorderSide(
                                            color: AppColors.dark2,
                                          ),
                                        ),
                                        focusedBorder: OutlineInputBorder(
                                          borderRadius:
                                              BorderRadius.circular(6),
                                          borderSide: BorderSide(
                                            color: AppColors.gold,
                                            width: 2,
                                          ),
                                        ),
                                        filled: true,
                                        fillColor: AppColors.dark3,
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 10,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    // Company Input
                                    TextField(
                                      controller: jobCompanyController,
                                      style: AppTypography.bodySmall.copyWith(
                                        color: AppColors.cream,
                                      ),
                                      decoration: InputDecoration(
                                        labelText: 'Company (Optional)',
                                        labelStyle:
                                            AppTypography.bodySmall.copyWith(
                                          color: AppColors.textSecondary,
                                          fontSize: 12,
                                        ),
                                        hintText: 'e.g. TechCorp Inc',
                                        hintStyle:
                                            AppTypography.bodySmall.copyWith(
                                          color: AppColors.textSecondary,
                                          fontSize: 11,
                                        ),
                                        border: OutlineInputBorder(
                                          borderRadius:
                                              BorderRadius.circular(6),
                                          borderSide: BorderSide(
                                            color: AppColors.dark2,
                                          ),
                                        ),
                                        focusedBorder: OutlineInputBorder(
                                          borderRadius:
                                              BorderRadius.circular(6),
                                          borderSide: BorderSide(
                                            color: AppColors.gold,
                                            width: 2,
                                          ),
                                        ),
                                        filled: true,
                                        fillColor: AppColors.dark3,
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 10,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    // Job Description Input
                                    Text(
                                      'Job Description *',
                                      style: AppTypography.bodySmall.copyWith(
                                        color: AppColors.cream,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Container(
                                      constraints: BoxConstraints(
                                        minHeight: 120,
                                        maxHeight: 150,
                                      ),
                                      child: TextField(
                                        controller:
                                            jobDescriptionController,
                                        maxLines: null,
                                        expands: true,
                                        textAlignVertical:
                                            TextAlignVertical.top,
                                        style: AppTypography.bodySmall
                                            .copyWith(
                                          color: AppColors.cream,
                                          height: 1.4,
                                        ),
                                        decoration: InputDecoration(
                                          hintText:
                                              'Paste job description or posting here...',
                                          hintStyle: AppTypography.bodySmall
                                              .copyWith(
                                            color: AppColors.textSecondary,
                                            fontSize: 11,
                                          ),
                                          border: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(6),
                                            borderSide: BorderSide(
                                              color: AppColors.dark2,
                                            ),
                                          ),
                                          focusedBorder: OutlineInputBorder(
                                            borderRadius:
                                                BorderRadius.circular(6),
                                            borderSide: BorderSide(
                                              color: AppColors.gold,
                                              width: 2,
                                            ),
                                          ),
                                          filled: true,
                                          fillColor: AppColors.dark3,
                                          contentPadding:
                                              const EdgeInsets.all(12.0),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 16),
                                    // Tailor Button
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton.icon(
                                        onPressed: isTailoring
                                            ? null
                                            : _tailorResume,
                                        icon: isTailoring
                                            ? SizedBox(
                                                width: 16,
                                                height: 16,
                                                child:
                                                    CircularProgressIndicator(
                                                  strokeWidth: 2,
                                                  valueColor:
                                                      AlwaysStoppedAnimation<
                                                          Color>(
                                                    AppColors.darkPrimary,
                                                  ),
                                                ),
                                              )
                                            : Icon(Icons.edit_outlined),
                                        label: Text(
                                          isTailoring
                                              ? 'Tailoring...'
                                              : 'Tailor Resume',
                                        ),
                                        style:
                                            ElevatedButton.styleFrom(
                                          backgroundColor: AppColors.gold,
                                          foregroundColor:
                                              AppColors.darkPrimary,
                                          disabledBackgroundColor:
                                              AppColors.dark3,
                                          disabledForegroundColor:
                                              AppColors.textSecondary,
                                          padding: const EdgeInsets.symmetric(
                                            vertical: 12,
                                          ),
                                        ),
                                      ),
                                    ),
                                    if (hasTailored) ...[
                                      const SizedBox(height: 24),
                                      Divider(
                                        height: 1,
                                        color: AppColors.dark2,
                                      ),
                                      const SizedBox(height: 16),
                                      Row(
                                        children: [
                                          Icon(
                                            Icons.check_circle,
                                            color: AppColors.successGreen,
                                            size: 20,
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            'Keyword Matches',
                                            style: AppTypography.labelText
                                                .copyWith(
                                              color: AppColors.cream,
                                              fontSize: 13,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 16),
                                      ListView.builder(
                                        shrinkWrap: true,
                                        physics:
                                            const NeverScrollableScrollPhysics(),
                                        itemCount: tailorMatches.length,
                                        itemBuilder: (context, index) {
                                          final match =
                                              tailorMatches[index];
                                          final isHighRelevance = int.parse(
                                                  match.relevance
                                                      .replaceAll('%', '')) >=
                                              90;

                                          return Container(
                                            margin: const EdgeInsets.only(
                                                bottom: 12),
                                            padding:
                                                const EdgeInsets.all(12),
                                            decoration: BoxDecoration(
                                              color: AppColors.dark3,
                                              border: Border.all(
                                                color: isHighRelevance
                                                    ? AppColors.gold
                                                        .withOpacity(0.3)
                                                    : AppColors.dark2,
                                              ),
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                            ),
                                            child: Column(
                                              crossAxisAlignment:
                                                  CrossAxisAlignment.start,
                                              children: [
                                                Text(
                                                  match.category,
                                                  style: AppTypography
                                                      .bodySmall
                                                      .copyWith(
                                                    color: AppColors
                                                        .textSecondary,
                                                    fontSize: 9,
                                                    fontWeight:
                                                        FontWeight.w500,
                                                  ),
                                                ),
                                                const SizedBox(height: 4),
                                                Row(
                                                  mainAxisAlignment:
                                                      MainAxisAlignment
                                                          .spaceBetween,
                                                  children: [
                                                    Expanded(
                                                      child: Text(
                                                        match.keyword,
                                                        style: AppTypography
                                                            .labelText
                                                            .copyWith(
                                                          color: AppColors
                                                              .cream,
                                                          fontSize: 11,
                                                          fontWeight:
                                                              FontWeight
                                                                  .w500,
                                                        ),
                                                        maxLines: 2,
                                                        overflow:
                                                            TextOverflow
                                                                .ellipsis,
                                                      ),
                                                    ),
                                                    const SizedBox(width: 8),
                                                    Container(
                                                      padding:
                                                          const EdgeInsets
                                                              .symmetric(
                                                        horizontal: 8,
                                                        vertical: 4,
                                                      ),
                                                      decoration:
                                                          BoxDecoration(
                                                        color: isHighRelevance
                                                            ? AppColors
                                                                .successGreen
                                                                .withOpacity(
                                                                    0.2)
                                                            : AppColors.dark2,
                                                        border: Border.all(
                                                          color: isHighRelevance
                                                              ? AppColors
                                                                  .successGreen
                                                              : Colors
                                                                  .transparent,
                                                        ),
                                                        borderRadius:
                                                            BorderRadius
                                                                .circular(3),
                                                      ),
                                                      child: Text(
                                                        match.relevance,
                                                        style: AppTypography
                                                            .bodySmall
                                                            .copyWith(
                                                          color: isHighRelevance
                                                              ? AppColors
                                                                  .successGreen
                                                              : AppColors
                                                                  .textSecondary,
                                                          fontSize: 9,
                                                          fontWeight:
                                                              FontWeight.w600,
                                                        ),
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ],
                                            ),
                                          );
                                        },
                                      ),
                                      const SizedBox(height: 12),
                                      SizedBox(
                                        width: double.infinity,
                                        child: ElevatedButton.icon(
                                          onPressed: _resetTailor,
                                          icon: Icon(
                                              Icons.refresh_outlined),
                                          label: Text('Try Again'),
                                          style:
                                              ElevatedButton.styleFrom(
                                            backgroundColor:
                                                AppColors.dark2,
                                            foregroundColor:
                                                AppColors.cream,
                                            padding: const EdgeInsets
                                                .symmetric(
                                              vertical: 10,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                ),
        // Vertical Divider
        Container(
          width: 1,
          color: AppColors.dark2,
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
                          Icons.file_copy_outlined,
                          size: 64,
                          color: AppColors.textSecondary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'No resumes available',
                          style: AppTypography.bodyLarge.copyWith(
                            color: AppColors.textSecondary,
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
                          color: AppColors.darkSecondary,
                          border: Border(
                            bottom: BorderSide(
                              color: AppColors.dark2,
                            ),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Resume Preview',
                              style: AppTypography.labelText.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              ResumeFileService.getFileName(
                                resumeFiles[selectedResumeIndex].path,
                              ),
                              style: AppTypography.bodySmall.copyWith(
                                color: AppColors.cream,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                      // PDF Viewer
                      Expanded(
                        child: Stack(
                          children: [
                            SfPdfViewer.file(
                              resumeFiles[selectedResumeIndex],
                              pageLayoutMode: PdfPageLayoutMode.continuous,
                            ),
                            if (isTailoring)
                              Container(
                                color: Colors.black.withOpacity(0.3),
                                child: Center(
                                  child: Column(
                                    mainAxisAlignment:
                                        MainAxisAlignment.center,
                                    children: [
                                      CircularProgressIndicator(
                                        color: AppColors.gold,
                                      ),
                                      const SizedBox(height: 16),
                                      Text(
                                        'Tailoring resume...',
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
                    ],
                  ),
          ),
        ),
      ],
    );
  }
}
