import 'package:flutter/material.dart';
import 'dart:io';
import 'package:url_launcher/url_launcher.dart';
import 'package:file_picker/file_picker.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../services/resume_file_service.dart';
import '../services/api_service.dart';
import '../models/resume_model.dart';

// ============================================================================
// MyResumesScreen StatefulWidget
// ============================================================================
class MyResumesScreen extends StatefulWidget {
  const MyResumesScreen({Key? key}) : super(key: key);

  @override
  State<MyResumesScreen> createState() => _MyResumesScreenState();
}
// ============================================================================

// ============================================================================
// _MyResumesScreenState
// ============================================================================
class _MyResumesScreenState extends State<MyResumesScreen> {
  /* STATE VARIABLES */
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isAddingResume = false;
  bool isGrading = false;
  GradeData? gradeData;
  String? gradeError;
  final ApiService _apiService = ApiService();

  // --------------------------------------------------------------------------
  // LIFECYCLE: initState
  // --------------------------------------------------------------------------
  @override
  void initState() {
    super.initState();
    _loadResumeFiles();
  }

  // --------------------------------------------------------------------------
  // METHOD: Load Resume Files
  // --------------------------------------------------------------------------
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

  // --------------------------------------------------------------------------
  // METHOD: Add Resume
  // --------------------------------------------------------------------------
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
        final resumesFolderPath = await ResumeFileService.getResumesFolderPath();
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

  // --------------------------------------------------------------------------
  // METHOD: Open Resume File
  // --------------------------------------------------------------------------
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

  // --------------------------------------------------------------------------
  // METHOD: Grade Resume
  // --------------------------------------------------------------------------
  Future<void> _gradeResume() async {
    if (resumeFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No resume selected'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      isGrading = true;
      gradeError = null;
    });

    try {
      // Get the filename of the selected resume
      final resumeFile = resumeFiles[selectedResumeIndex];
      final filename = resumeFile.path.split('/').last;

      // Call API to grade using filename (backend will extract PDF text if needed)
      final response = await _apiService.gradeResume(filename);

      if (mounted) {
        if (response.success && response.grade != null) {
          setState(() {
            gradeData = response.grade;
            gradeError = null;
            isGrading = false;
          });

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Resume graded: ${response.grade!.score}/100'),
              backgroundColor: AppColors.successGreen,
            ),
          );
        } else {
          setState(() {
            gradeError = response.error ?? 'Failed to grade resume';
            gradeData = null;
            isGrading = false;
          });

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(gradeError ?? 'Failed to grade resume'),
              backgroundColor: AppColors.errorRed,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          gradeError = 'Error: $e';
          gradeData = null;
          isGrading = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(gradeError ?? 'Error grading resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Get File Size Text
  // --------------------------------------------------------------------------
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

  // --------------------------------------------------------------------------
  // HELPER BUILD: Loading State
  // --------------------------------------------------------------------------
  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.gold),
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
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Empty State
  // --------------------------------------------------------------------------
  Widget _buildEmptyState() {
    return Column(
      children: [
        Expanded(
          child: Center(
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
                  'Add your first resume to get started',
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textTertiary,
                  ),
                ),
              ],
            ),
          ),
        ),
        _buildAddResumeButton(),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Resume List Content
  // --------------------------------------------------------------------------
  Widget _buildResumeListContent() {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
            itemCount: resumeFiles.length,
            itemBuilder: (context, index) {
              return _buildResumeListItem(index);
            },
          ),
        ),
        _buildAddResumeButton(),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Resume List Item
  // --------------------------------------------------------------------------
  Widget _buildResumeListItem(int index) {
    final isSelected = selectedResumeIndex == index;
    final fileName = ResumeFileService.getFileName(resumeFiles[index].path);
    final lastModified = ResumeFileService.getLastModified(resumeFiles[index]);
    final fileSize = _getFileSizeText(resumeFiles[index]);

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedResumeIndex = index;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.dark3 : AppColors.dark2,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? AppColors.gold : AppColors.dark3,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.picture_as_pdf,
                  color: AppColors.errorRed,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    fileName,
                    style: AppTypography.labelText.copyWith(
                      color: AppColors.cream,
                      fontSize: 12,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  lastModified,
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontSize: 10,
                  ),
                ),
                Text(
                  fileSize,
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textTertiary,
                    fontSize: 9,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Add Resume Button
  // --------------------------------------------------------------------------
  Widget _buildAddResumeButton() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: isAddingResume ? null : _addResume,
          icon: isAddingResume
              ? SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isAddingResume
                          ? AppColors.darkPrimary
                          : AppColors.darkPrimary,
                    ),
                    strokeWidth: 2,
                  ),
                )
              : const Icon(Icons.add),
          label: Text(
            isAddingResume ? 'Adding...' : 'Add Resume',
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.gold,
            foregroundColor: AppColors.darkPrimary,
            padding: const EdgeInsets.symmetric(vertical: 12),
            disabledBackgroundColor: AppColors.dark3,
            disabledForegroundColor: AppColors.textSecondary,
          ),
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Grade Score Container with Insights
  // --------------------------------------------------------------------------
  Widget _buildGradeScoreContainer() {
    if (gradeError != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: AppColors.errorRed,
            ),
            const SizedBox(height: 12),
            Text(
              'Grade Unavailable',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              gradeError ?? 'Unknown error',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.textSecondary,
                fontSize: 11,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    if (gradeData == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.assessment_outlined,
              size: 48,
              color: AppColors.textSecondary,
            ),
            const SizedBox(height: 12),
            Text(
              'No Grade Yet',
              style: AppTypography.labelText.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Click "Get Fresh Grade" to analyze',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.textTertiary,
                fontSize: 11,
              ),
            ),
          ],
        ),
      );
    }

    // Display actual grade data
    final score = gradeData!.score;
    final scoreLabel = score >= 80
        ? 'Excellent'
        : score >= 70
            ? 'Good'
            : score >= 60
                ? 'Fair'
                : 'Needs Work';
    final scoreColor = score >= 80
        ? AppColors.successGreen
        : score >= 70
            ? AppColors.gold
            : AppColors.errorRed;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Overall Score Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Overall Score',
                  style: AppTypography.labelText.copyWith(
                    color: AppColors.cream,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  scoreLabel,
                  style: AppTypography.bodySmall.copyWith(
                    color: scoreColor,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
            Text(
              '${score}/100',
              style: AppTypography.headingPageTitle.copyWith(
                color: scoreColor,
                fontSize: 28,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Insights Section (Scrollable, fixed height)
        SizedBox(
          height: 105,
          child: _buildInsightsPanel(),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Insights Panel (Comparing to Industry Standard)
  // --------------------------------------------------------------------------
  Widget _buildInsightsPanel() {
    if (gradeData == null) {
      return SizedBox.shrink();
    }

    // Display strengths and improvements
    final items = <Map<String, dynamic>>[
      ...gradeData!.strengths.asMap().entries.map((e) => {
        'title': 'Strength ${e.key + 1}',
        'value': e.value,
        'color': AppColors.successGreen,
        'icon': Icons.check_circle,
      }),
      ...gradeData!.improvements.asMap().entries.map((e) => {
        'title': 'Improvement ${e.key + 1}',
        'value': e.value,
        'color': AppColors.gold,
        'icon': Icons.lightbulb,
      }),
    ];

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.dark2,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.dark3),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: List.generate(
            items.length,
            (index) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    items[index]['icon'] as IconData,
                    size: 14,
                    color: items[index]['color'] as Color,
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          items[index]['title'] as String,
                          style: AppTypography.bodySmall.copyWith(
                            color: items[index]['color'] as Color,
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          items[index]['value'] as String,
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                            fontSize: 9,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Grade Button
  // --------------------------------------------------------------------------
  Widget _buildGradeButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: isGrading ? null : _gradeResume,
        icon: isGrading
            ? SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppColors.darkPrimary.withOpacity(0.7),
                  ),
                ),
              )
            : const Icon(Icons.assessment),
        label: Text(isGrading ? 'Grading...' : 'Get Fresh Grade'),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.gold,
          foregroundColor: AppColors.darkPrimary,
          padding: const EdgeInsets.symmetric(vertical: 12),
          disabledBackgroundColor: AppColors.gold.withOpacity(0.5),
          disabledForegroundColor: AppColors.darkPrimary.withOpacity(0.5),
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: No Resumes Preview Panel
  // --------------------------------------------------------------------------
  Widget _buildNoResumesPreviewPanel() {
    return Center(
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
    );
  }

  // --------------------------------------------------------------------------
  // HELPER BUILD: Resume Preview Panel
  // --------------------------------------------------------------------------
  Widget _buildResumePreviewPanel() {
    return Container(
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
          // Preview Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(color: AppColors.gold.withOpacity(0.3)),
              ),
            ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
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
              ),
            ],
          ),
        ),

        // PDF Viewer Content
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.dark3),
            ),
            margin: const EdgeInsets.all(12),
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
    );
  }

  // --------------------------------------------------------------------------
  // BUILD: Main Widget Tree
  // --------------------------------------------------------------------------
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // ====================================================================
        // LEFT PANEL: Resume List & Grade (40%)
        // ====================================================================
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ==============================================================
                // SECTION 1: My Resumes # Resumes (Resume List)
                // ==============================================================
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
                                '${resumeFiles.length} Resume',
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
                              ? _buildLoadingState()
                              : resumeFiles.isEmpty
                                  ? _buildEmptyState()
                                  : _buildResumeListContent(),
                        ),
                      ],
                    ),
                  ),
                ),

                // Vertical Divider
                Container(
                  height: 1,
                  color: AppColors.dark3,
                ),

                // ==============================================================
                // SECTION 2: Resume Grade
                // ==============================================================
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
                          padding: const EdgeInsets.all(10.0),
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
                            padding: const EdgeInsets.all(12.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _buildGradeScoreContainer(),
                                const SizedBox(height: 8),
                                _buildGradeButton(),
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

        // ====================================================================
        // VERTICAL DIVIDER
        // ====================================================================
        Container(
          width: 1,
          color: AppColors.dark3,
        ),

        // ====================================================================
        // RIGHT PANEL: Resume Preview (60%)
        // ====================================================================
        Expanded(
          flex: 60,
          child: Container(
            color: AppColors.darkPrimary,
            child: resumeFiles.isEmpty
                ? _buildNoResumesPreviewPanel()
                : _buildResumePreviewPanel(),
          ),
        ),
      ],
    );
  }
}
// ============================================================================