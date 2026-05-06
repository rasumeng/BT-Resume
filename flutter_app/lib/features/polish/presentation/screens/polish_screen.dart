import 'package:flutter/material.dart';
import 'dart:io';
import 'package:logger/logger.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../../../../config/colors.dart';
import '../../../../config/typography.dart';
import '../../../../core/services/resume_file_service.dart';
import '../../../../core/services/api_service.dart';
import '../../../../shared/widgets/download_dialog.dart';

// ============================================================================
// PolishChange Model
// ============================================================================
class PolishChange {
  /* MEMBERS */
  final String icon;
  final String title;
  final String description;

  /* CONSTRUCTOR */
  PolishChange({
    required this.icon,
    required this.title,
    required this.description,
  });
}
// ============================================================================

// ============================================================================
// PolishScreen StatefulWidget
// ============================================================================
class PolishScreen extends StatefulWidget {
  const PolishScreen({Key? key}) : super(key: key);

  @override
  State<PolishScreen> createState() => _PolishScreenState();
}
// ============================================================================

// ============================================================================
// _PolishScreenState
// ============================================================================
class _PolishScreenState extends State<PolishScreen> {
  /* STATE VARIABLES */
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isPolishing = false;
  bool hasPolished = false;
  bool isGeneratingPdf = false;
  List<PolishChange> polishChanges = [];
  File? polishedPdfFile; // Track the polished PDF for preview and download
  String? polishedResumeContent; // Store polished content for PDF generation
  final ApiService _apiService = ApiService();
  final logger = Logger();

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
  // METHOD: Polish Resume
  // --------------------------------------------------------------------------
  Future<void> _polishResume() async {
    if (resumeFiles.isEmpty || selectedResumeIndex >= resumeFiles.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Please select a resume to polish'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    try {
      setState(() {
        isPolishing = true;
      });

      // Extract text from the selected PDF file
      final selectedFile = resumeFiles[selectedResumeIndex];
      logger.i('Extracting text from: ${selectedFile.path}');
      
      final resumeContent = await _apiService.extractPdfText(selectedFile);

      // Parse and cache the resume structure for reuse
      logger.i('📄 Parsing resume into structured format...');
      try {
        await _apiService.parseAndCacheResume(
          resumeContent,
          filename: selectedFile.path.split(Platform.pathSeparator).last,
        );
      } catch (parseError) {
        logger.w('⚠️  Failed to cache parsed resume (non-critical): $parseError');
        // Continue anyway - polish will still work with raw text
      }

      // Call API to polish the resume
      final polishedContent = await _apiService.polishResume(
        resumeContent,
        intensity: 'medium',
      );

      // polishedContent is already a String
      final polishedText = polishedContent;

      // Generate professional PDF from polished content using template
      logger.i('📄 Generating professional PDF from polished content...');
      try {
        final timestamp = DateTime.now().millisecondsSinceEpoch;
        // Backend will add "polished_" prefix automatically
        final pdfFilename = 'resume_$timestamp.pdf';
        
        // Use saveTextPdf endpoint which now generates professional PDFs using template
        // The backend parses the text, structures it, and generates using pdf_generator
        final saveResult = await _apiService.saveTextPdf(pdfFilename, polishedText);
        
        // Verify backend saved the file successfully
        if (!saveResult['success']) {
          throw Exception('Backend failed to save PDF: ${saveResult['error']}');
        }
        
        // Use the path from backend response - it knows the actual OS path
        final polishedPdfPath = saveResult['path'];
        if (polishedPdfPath == null || polishedPdfPath.isEmpty) {
          throw Exception('Backend response missing path information');
        }
        
        final polishedPdfFileTemp = File(polishedPdfPath);
        
        // Verify the file was actually created at the backend's reported path
        if (!await polishedPdfFileTemp.exists()) {
          logger.e('❌ File check failed at: $polishedPdfPath');
          logger.e('Backend reported file at: $polishedPdfPath');
          throw Exception('Polished PDF file was not created at: $polishedPdfPath');
        }
        
        logger.i('✅ Professional polished resume PDF generated: $polishedPdfPath');

        // Get real changes from backend
        List<String> changesFromBackend = [];
        try {
          changesFromBackend = await _apiService.getPolishChanges(
            resumeContent,
            polishedText,
          );
          logger.i('✓ Got ${changesFromBackend.length} real polish changes');
        } catch (e) {
          logger.w('⚠️  Failed to get polish changes: $e');
          // Will use fallback changes below
        }

        // Convert change descriptions to PolishChange objects
        List<PolishChange> realChanges = changesFromBackend.isNotEmpty
            ? changesFromBackend
                .map((change) => PolishChange(
                  icon: '✓',
                  title: change.length > 60 ? change.substring(0, 60) + '...' : change,
                  description: change,
                ))
                .toList()
            : [
                // Fallback if no changes returned
                PolishChange(
                  icon: '✓',
                  title: 'Content enhanced',
                  description: 'Resume content optimized for clarity and impact',
                ),
                PolishChange(
                  icon: '✓',
                  title: 'Formatting improved',
                  description: 'Professional formatting for ATS compatibility',
                ),
              ];

        setState(() {
          hasPolished = true;
          isPolishing = false;
          polishedPdfFile = polishedPdfFileTemp;
          polishedResumeContent = polishedText;
          polishChanges = realChanges;
        });
      } catch (pdfError) {
        logger.e('❌ Error generating polished PDF: $pdfError');
        logger.e('Stack trace: $pdfError');
        // DON'T continue silently - user needs to know PDF generation failed
        setState(() {
          isPolishing = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error generating polished resume PDF: $pdfError'),
              backgroundColor: AppColors.errorRed,
              duration: const Duration(seconds: 5),
            ),
          );
        }
        rethrow;  // Re-throw to propagate error
      }
    } catch (e) {
      logger.e('Error polishing resume: $e');
      setState(() {
        isPolishing = false;
      });
      if (mounted) {
        String errorMessage = 'Error polishing resume';
        
        // Provide user-friendly error messages
        if (e.toString().contains('404')) {
          errorMessage = 'Backend endpoint not found. Ensure backend is running.';
        } else if (e.toString().contains('Backend is not responding')) {
          errorMessage = 'Cannot connect to backend. Please start the Flask backend.';
        } else if (e.toString().contains('Connection refused')) {
          errorMessage = 'Connection refused. Ensure backend is running on localhost:5000.';
        } else if (e.toString().contains('timeout')) {
          errorMessage = 'Backend request timed out. Please try again.';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: AppColors.errorRed,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Reset Polish State
  // --------------------------------------------------------------------------
  void _resetPolish() {
    setState(() {
      hasPolished = false;
      polishChanges = [];
      polishedPdfFile = null; // Clear polished PDF when switching resumes
      polishedResumeContent = null;
    });
  }

  // --------------------------------------------------------------------------
  // METHOD: Generate PDF from Polished Resume
  // --------------------------------------------------------------------------
  Future<void> _generatePdf() async {
    if (resumeFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No resume selected'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Show dialog to input filename
    final fileName = await _showPdfFilenameDialog();
    if (fileName == null || fileName.isEmpty) return;

    setState(() {
      isGeneratingPdf = true;
    });

    try {
      // Sample resume data - in production, this would be parsed from the PDF
      final sampleResumeData = {
        'contact': {
          'name': 'John Doe',
          'email': 'john@example.com',
          'phone': '(555) 123-4567',
          'location': 'Boston, MA',
          'linkedin': 'linkedin.com/in/johndoe',
        },
        'education': [
          {
            'school': 'Massachusetts Institute of Technology',
            'degree': 'BS Computer Science',
            'location': 'Cambridge, MA',
            'date': '2020',
            'details': ['Graduated with honors', 'GPA: 3.8']
          }
        ],
        'skills': [
          {
            'category': 'Programming Languages',
            'items': ['Python', 'JavaScript', 'Java', 'C++']
          },
          {
            'category': 'Tools & Frameworks',
            'items': ['Flutter', 'React', 'Django', 'TensorFlow']
          }
        ],
        'work_experience': [
          {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Boston, MA',
            'start_date': '2020',
            'end_date': '2023',
            'bullets': [
              'Led team of 5 engineers in building scalable microservices',
              'Improved system performance by 40% through optimization',
              'Mentored 3 junior developers in best practices'
            ]
          },
          {
            'title': 'Junior Developer',
            'company': 'StartupXYZ',
            'location': 'Remote',
            'start_date': '2019',
            'end_date': '2020',
            'bullets': [
              'Developed full-stack web application using React and Django',
              'Implemented CI/CD pipeline reducing deployment time by 50%',
              'Collaborated with design team on UI/UX improvements'
            ]
          }
        ],
        'projects': [
          {
            'name': 'Resume AI',
            'details': ['AI-powered resume analyzer and generator', 'Built with Flutter and Python']
          }
        ]
      };

      // Call API to generate PDF
      final pdfFilename = fileName.endsWith('.pdf') ? fileName : '$fileName.pdf';
      final result = await _apiService.savePdf(pdfFilename, sampleResumeData);

      if (mounted) {
        setState(() {
          isGeneratingPdf = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('PDF generated: $result'),
            backgroundColor: AppColors.successGreen,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          isGeneratingPdf = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error generating PDF: $e'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Show PDF Filename Dialog
  // --------------------------------------------------------------------------
  Future<String?> _showPdfFilenameDialog() async {
    final TextEditingController controller = TextEditingController(
      text: 'polished_resume_${DateTime.now().millisecondsSinceEpoch}',
    );

    return showDialog<String?>(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        backgroundColor: AppColors.dark2,
        title: Text(
          'Export Polished Resume as PDF',
          style: AppTypography.labelText.copyWith(color: AppColors.cream),
        ),
        content: TextField(
          controller: controller,
          style: AppTypography.bodySmall.copyWith(color: AppColors.cream),
          decoration: InputDecoration(
            hintText: 'Enter filename',
            hintStyle: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
            border: OutlineInputBorder(
              borderSide: BorderSide(color: AppColors.gold),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(color: AppColors.gold, width: 2),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: AppTypography.bodySmall.copyWith(color: AppColors.textSecondary),
            ),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.gold,
              foregroundColor: AppColors.darkPrimary,
            ),
            onPressed: () => Navigator.pop(context, controller.text),
            child: Text(
              'Generate',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.darkPrimary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // METHOD: Open Resume File
  // --------------------------------------------------------------------------
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
  // BUILD: Main Widget Tree
  // --------------------------------------------------------------------------
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // ====================================================================
        // LEFT PANEL: Resume List (40%)
        // ====================================================================
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ==============================================================
                // SECTION 1: Resume List with Header
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
                        // ======================================================
                        // HEADER: Title and Count
                        // ======================================================
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
                        // ======================================================
                        // DIVIDER: Under Header
                        // ======================================================
                        Container(
                          height: 1,
                          color: AppColors.gold.withOpacity(0.3),
                        ),
                        // ======================================================
                        // CONTENT: Resume List or Empty State
                        // ======================================================
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

                // ==============================================================
                // DIVIDER: Between Sections
                // ==============================================================
                Container(
                  height: 1,
                  color: AppColors.dark3,
                ),

                // ==============================================================
                // SECTION 2: Polish Changes/Summary Section
                // ==============================================================
                Expanded(
                  flex: 30,
                  child: _buildPolishSummarySection(),
                ),


              ],
            ),
          ),
        ),

        // ====================================================================
        // VERTICAL DIVIDER: Between Panels
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
              ? _buildNoResumeSelectedPanel()
              : _buildResumePreviewPanel(),
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Loading State
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
  // BUILD HELPER: Empty State
  // --------------------------------------------------------------------------
  Widget _buildEmptyState() {
    return Center(
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
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Resume List Content
  // --------------------------------------------------------------------------
  Widget _buildResumeListContent() {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
            itemCount: resumeFiles.length,
            itemBuilder: (context, index) => _buildResumeListItem(index),
          ),
        ),
        _buildIntensityExplanation(),
        _buildPolishResumeButton(),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Single Resume List Item
  // --------------------------------------------------------------------------
  Widget _buildResumeListItem(int index) {
    return GestureDetector(
      onTap: () {
        setState(() {
          selectedResumeIndex = index;
          _resetPolish();
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: selectedResumeIndex == index ? AppColors.dark3 : AppColors.dark2,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: selectedResumeIndex == index ? AppColors.gold : AppColors.dark3,
            width: selectedResumeIndex == index ? 2 : 1,
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
                    ResumeFileService.getFileName(resumeFiles[index].path),
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
                  ResumeFileService.getLastModified(resumeFiles[index]),
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontSize: 10,
                  ),
                ),
                Text(
                  _getFileSizeText(resumeFiles[index]),
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

  // BUILD HELPER: Intensity Explanation
  // --------------------------------------------------------------------------
  Widget _buildIntensityExplanation() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.dark3.withOpacity(0.6),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: AppColors.gold.withOpacity(0.2),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Polish Intensity: Medium',
              style: AppTypography.bodyLarge.copyWith(
                color: AppColors.cream,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Improve clarity and impact. Reframe for better readability while preserving all original accomplishments.',
              style: AppTypography.bodyNormal.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Polish Resume Button
  // --------------------------------------------------------------------------
  Widget _buildPolishResumeButton() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: resumeFiles.isEmpty || isPolishing ? null : _polishResume,
          icon: isPolishing
              ? SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isPolishing
                          ? AppColors.darkPrimary
                          : AppColors.darkPrimary,
                    ),
                    strokeWidth: 2,
                  ),
                )
              : const Icon(Icons.brush),
          label: Text(
            isPolishing ? 'Polishing...' : 'Polish Resume',
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
  // BUILD HELPER: Polish Summary Section (Combined Preview + Results)
  // --------------------------------------------------------------------------
  Widget _buildPolishSummarySection() {
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ======================================================
          // HEADER: Title (Updates based on state)
          // ======================================================
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'Improvements',
                      style: AppTypography.labelText.copyWith(
                        color: AppColors.cream,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (hasPolished) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.successGreen.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: AppColors.successGreen.withOpacity(0.5),
                          ),
                        ),
                        child: Text(
                          'Applied',
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.successGreen,
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  hasPolished
                      ? 'Here\'s what we improved in your resume'
                      : 'Potential improvements we can make',
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          // ======================================================
          // DIVIDER: Under Header
          // ======================================================
          Container(
            height: 1,
            color: AppColors.gold.withOpacity(0.3),
          ),
          // ======================================================
          // CONTENT: Combined Preview + Results
          // ======================================================
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: hasPolished
                    ? _buildCombinedChanges()
                    : _buildPreviewItems(),
              ),
            ),
          ),
          // ======================================================
          // FOOTER: Export Button (Only show if polished)
          // ======================================================
          if (hasPolished) ...[
            Container(
              height: 1,
              color: AppColors.gold.withOpacity(0.3),
            ),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: isGeneratingPdf ? null : _generatePdf,
                  icon: isGeneratingPdf
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
                      : const Icon(Icons.download),
                  label: Text(isGeneratingPdf ? 'Generating...' : 'Export as PDF'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.successGreen,
                    foregroundColor: AppColors.darkPrimary,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    disabledBackgroundColor: AppColors.successGreen.withOpacity(0.5),
                    disabledForegroundColor: AppColors.darkPrimary.withOpacity(0.5),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Preview Items (Before Polish)
  // --------------------------------------------------------------------------
  Widget _buildPreviewItems() {
    final previewItems = [
      {
        'icon': '✓',
        'title': 'Action Verbs Enhanced',
        'description': 'Replace weak verbs with powerful alternatives',
      },
      {
        'icon': '✓',
        'title': 'Metrics & Numbers',
        'description': 'Quantify achievements with impact metrics',
      },
      {
        'icon': '✓',
        'title': 'Clarity Improved',
        'description': 'Enhance readability and professionalism',
      },
      {
        'icon': '✓',
        'title': 'ATS Optimized',
        'description': 'Better keyword matching for applicant tracking',
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(
        previewItems.length,
        (index) {
          final item = previewItems[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 12.0),
            child: _buildSummaryItem(
              icon: item['icon']!,
              title: item['title']!,
              description: item['description']!,
              isApplied: false,
            ),
          );
        },
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Combined Changes (After Polish)
  // --------------------------------------------------------------------------
  Widget _buildCombinedChanges() {
    final defaultItems = [
      {
        'icon': '✓',
        'title': 'Action Verbs Enhanced',
        'description': 'Replace weak verbs with powerful alternatives',
      },
      {
        'icon': '✓',
        'title': 'Metrics & Numbers',
        'description': 'Quantify achievements with impact metrics',
      },
      {
        'icon': '✓',
        'title': 'Clarity Improved',
        'description': 'Enhance readability and professionalism',
      },
      {
        'icon': '✓',
        'title': 'ATS Optimized',
        'description': 'Better keyword matching for applicant tracking',
      },
    ];

    // Use actual changes if available, otherwise show defaults
    final itemsToShow = polishChanges.isNotEmpty
        ? polishChanges.map((change) {
            return {
              'icon': change.icon,
              'title': change.title,
              'description': change.description,
            };
          }).toList()
        : defaultItems;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(
        itemsToShow.length,
        (index) {
          final item = itemsToShow[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 12.0),
            child: _buildSummaryItem(
              icon: item['icon']!,
              title: item['title']!,
              description: item['description']!,
              isApplied: true,
            ),
          );
        },
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Summary Item (with Applied State)
  // --------------------------------------------------------------------------
  Widget _buildSummaryItem({
    required String icon,
    required String title,
    required String description,
    bool isApplied = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: isApplied ? AppColors.dark3 : AppColors.dark2,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: isApplied
              ? AppColors.successGreen.withOpacity(0.3)
              : AppColors.gold.withOpacity(0.2),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: isApplied
                  ? AppColors.successGreen.withOpacity(0.2)
                  : AppColors.gold.withOpacity(0.2),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Center(
              child: Text(
                icon,
                style: TextStyle(
                  color: isApplied ? AppColors.successGreen : AppColors.gold,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTypography.labelText.copyWith(
                    color: AppColors.cream,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }



  // --------------------------------------------------------------------------
  // BUILD HELPER: No Resume Selected Panel
  // --------------------------------------------------------------------------
  Widget _buildNoResumeSelectedPanel() {
    return Center(
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
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Resume Preview Panel
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
          // ====================================================================
          // HEADER: Preview Title and Download Button
          // ====================================================================
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
                      'Professional template with AI enhancements',
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              _buildDownloadButton(),
            ],
          ),
        ),

        // ====================================================================
        // CONTENT: PDF Viewer with Overlay
        // ====================================================================
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.dark3),
            ),
            margin: const EdgeInsets.all(12),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Stack(
                children: [
                  SfPdfViewer.file(
                    polishedPdfFile ?? resumeFiles[selectedResumeIndex],
                    pageLayoutMode: PdfPageLayoutMode.continuous,
                  ),
                  if (isPolishing) _buildPolishingOverlay(),
                ],
              ),
            ),
          ),
        ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Download Button
  // --------------------------------------------------------------------------
  Widget _buildDownloadButton() {
    return IconButton(
      icon: const Icon(Icons.download),
      color: hasPolished ? AppColors.gold : AppColors.textTertiary,
      tooltip: hasPolished
          ? 'Download polished resume'
          : 'Polish resume to download',
      onPressed: hasPolished
          ? () => _downloadPolishedResume()
          : null,
    );
  }

  // --------------------------------------------------------------------------
  // METHOD: Download Polished Resume
  // --------------------------------------------------------------------------
  Future<void> _downloadPolishedResume() async {
    if (selectedResumeIndex >= resumeFiles.length) return;

    // Use polished PDF if available, otherwise fall back to original
    final sourceFile = polishedPdfFile ?? resumeFiles[selectedResumeIndex];
    final originalFileName = polishedPdfFile != null
        ? 'polished_resume'
        : ResumeFileService.getFileName(resumeFiles[selectedResumeIndex].path);

    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => DownloadDialog(
          originalFileName: originalFileName,
          onDownload: (fileName, replaceOriginal) async {
            await _performDownload(
              sourceFile,
              fileName,
              replaceOriginal,
              'polished',
            );
          },
        ),
      );
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Perform Download
  // --------------------------------------------------------------------------
  Future<void> _performDownload(
    File sourceFile,
    String fileName,
    bool replaceOriginal,
    String type,
  ) async {
    try {
      final downloadPath = await ResumeFileService.downloadResume(
        sourceFile,
        fileName,
        replaceOriginal: replaceOriginal,
      );

      if (mounted && downloadPath != null) {
        final message = replaceOriginal
            ? '✓ Resume replaced: $fileName.pdf'
            : '✓ Downloaded to: $fileName.pdf';

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: AppColors.successGreen,
            duration: const Duration(seconds: 3),
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✗ Failed to download resume'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✗ Error: ${e.toString()}'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Polishing Overlay
  // --------------------------------------------------------------------------
  Widget _buildPolishingOverlay() {
    return Container(
      color: AppColors.darkPrimary.withOpacity(0.7),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.gold),
            ),
            const SizedBox(height: 16),
            Text(
              'Polishing resume...',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.cream,
              ),
            ),
          ],
        ),
      ),
    );
  }
}