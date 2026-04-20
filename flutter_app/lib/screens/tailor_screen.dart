import 'package:flutter/material.dart';
import 'dart:io';
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../services/resume_file_service.dart';
import '../services/api_service.dart';
import '../widgets/download_dialog.dart';

// ============================================================================
// TailorMatch Model
// ============================================================================
class TailorMatch {
  /* MEMBERS */
  final String category;
  final String keyword;
  final String relevance;

  /* CONSTRUCTOR */
  TailorMatch({
    required this.category,
    required this.keyword,
    required this.relevance,
  });
}
// ============================================================================

// ============================================================================
// TailorScreen StatefulWidget
// ============================================================================
class TailorScreen extends StatefulWidget {
  const TailorScreen({Key? key}) : super(key: key);

  @override
  State<TailorScreen> createState() => _TailorScreenState();
}
// ============================================================================

// ============================================================================
// _TailorScreenState
// ============================================================================
class _TailorScreenState extends State<TailorScreen> {
  /* STATE VARIABLES */
  List<File> resumeFiles = [];
  int selectedResumeIndex = 0;
  bool isLoading = true;
  bool isTailoring = false;
  bool hasTailored = false;
  bool isGeneratingPdf = false;
  List<TailorMatch> tailorMatches = [];
  final ApiService _apiService = ApiService();

  /* TEXT CONTROLLERS */
  final TextEditingController jobPositionController = TextEditingController();
  final TextEditingController jobCompanyController = TextEditingController();
  final TextEditingController jobDescriptionController = TextEditingController();

  // --------------------------------------------------------------------------
  // LIFECYCLE: initState
  // --------------------------------------------------------------------------
  @override
  void initState() {
    super.initState();
    _loadResumeFiles();
  }

  // --------------------------------------------------------------------------
  // LIFECYCLE: dispose
  // --------------------------------------------------------------------------
  @override
  void dispose() {
    jobPositionController.dispose();
    jobCompanyController.dispose();
    jobDescriptionController.dispose();
    super.dispose();
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
  // METHOD: Tailor Resume
  // --------------------------------------------------------------------------
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

      // Simulate the process with mock data
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

  // --------------------------------------------------------------------------
  // METHOD: Reset Tailor State
  // --------------------------------------------------------------------------
  void _resetTailor() {
    setState(() {
      hasTailored = false;
      tailorMatches = [];
    });
  }

  // --------------------------------------------------------------------------
  // METHOD: Generate PDF from Tailored Resume
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
      text: 'tailored_resume_${DateTime.now().millisecondsSinceEpoch}',
    );

    return showDialog<String?>(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        backgroundColor: AppColors.dark2,
        title: Text(
          'Export Tailored Resume as PDF',
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
        // LEFT PANEL: Inputs & Results (40%)
        // ====================================================================
        Expanded(
          flex: 40,
          child: Container(
            color: AppColors.darkSecondary,
            child: isLoading
              ? _buildLoadingState()
              : resumeFiles.isEmpty
                ? _buildNoResumesPanel()
                : _buildLeftPanelContent(),
          ),
        ),

        // ====================================================================
        // VERTICAL DIVIDER: Between Panels
        // ====================================================================
        Container(
          width: 1,
          color: AppColors.dark2,
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

  // --------------------------------------------------------------------------
  // BUILD HELPER: Loading State
  // --------------------------------------------------------------------------
  Widget _buildLoadingState() {
    return Center(
      child: CircularProgressIndicator(
        color: AppColors.gold,
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: No Resumes Panel (Left)
  // --------------------------------------------------------------------------
  Widget _buildNoResumesPanel() {
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
  // BUILD HELPER: Left Panel Content (with Resume List & Job Details)
  // --------------------------------------------------------------------------
  Widget _buildLeftPanelContent() {
    return Column(
      children: [
        // ==============================================================
        // SECTION 1: Resume List
        // ==============================================================
        Expanded(
          flex: 45,
          child: _buildResumeListSection(),
        ),

        // ==============================================================
        // DIVIDER: Between Sections
        // ==============================================================
        Container(
          height: 1,
          color: AppColors.dark3,
        ),

        // ==============================================================
        // SECTION 2: Job Details & Results
        // ==============================================================
        Expanded(
          flex: 55,
          child: _buildJobDetailsSection(),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Resume List Section
  // --------------------------------------------------------------------------
  Widget _buildResumeListSection() {
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
        crossAxisAlignment: CrossAxisAlignment.center,
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
                  'Select Resume',
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
          // ======================================================
          // DIVIDER: Under Header
          // ======================================================
          Container(
            height: 1,
            color: AppColors.gold.withOpacity(0.3),
          ),
          // ======================================================
          // CONTENT: Resume List
          // ======================================================
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
              itemCount: resumeFiles.length,
              itemBuilder: (context, index) => _buildResumeListItem(index),
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Single Resume List Item
  // --------------------------------------------------------------------------
  Widget _buildResumeListItem(int index) {
    final file = resumeFiles[index];
    final isSelected = selectedResumeIndex == index;
    final fileName = ResumeFileService.getFileName(file.path);
    final lastModified = ResumeFileService.getLastModified(file);
    final fileSize = _getFileSizeText(file);

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
  // BUILD HELPER: Job Details Section
  // --------------------------------------------------------------------------
  Widget _buildJobDetailsSection() {
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
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // ======================================================
          // HEADER: Title and Description
          // ======================================================
          Padding(
            padding: const EdgeInsets.all(5.0),
            child: _buildJobDetailsHeader(),
          ),
          // ======================================================
          // DIVIDER: Under Header
          // ======================================================
          Container(
            height: 1,
            color: AppColors.gold.withOpacity(0.3),
          ),
          // ======================================================
          // CONTENT: Input Fields, Button, and Results
          // ======================================================
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildJobInputFields(),
                    // ======================================================
                    // BUTTON: Tailor Resume
                    // ======================================================
                    const SizedBox(height: 16),
                    _buildTailorButton(),
                    // ======================================================
                    // RESULTS: If Tailored
                    // ======================================================
                    if (hasTailored) _buildTailorResults(),
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
  // BUILD HELPER: Job Details Header
  // --------------------------------------------------------------------------
  Widget _buildJobDetailsHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(
          'Job Details',
          textAlign: TextAlign.center,
          style: AppTypography.labelText.copyWith(
            color: AppColors.cream,
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Enter job information to tailor your resume',
          textAlign: TextAlign.center,
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Job Input Fields
  // --------------------------------------------------------------------------
  Widget _buildJobInputFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Position Input
        TextField(
          controller: jobPositionController,
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.cream,
          ),
          decoration: InputDecoration(
            labelText: 'Job Position (Optional)',
            labelStyle: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
              fontSize: 12,
            ),
            hintText: 'e.g. Senior Product Manager',
            hintStyle: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
              fontSize: 11,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: BorderSide(color: AppColors.dark2),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: BorderSide(
                color: AppColors.gold,
                width: 2,
              ),
            ),
            filled: true,
            fillColor: AppColors.dark3,
            contentPadding: const EdgeInsets.symmetric(
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
            labelStyle: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
              fontSize: 12,
            ),
            hintText: 'e.g. TechCorp Inc',
            hintStyle: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
              fontSize: 11,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: BorderSide(color: AppColors.dark2),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: BorderSide(
                color: AppColors.gold,
                width: 2,
              ),
            ),
            filled: true,
            fillColor: AppColors.dark3,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 10,
            ),
          ),
        ),
        const SizedBox(height: 12),
        // Job Description Label
        Text(
          'Job Description *',
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.cream,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        // Job Description Input
        Container(
          constraints: BoxConstraints(
            minHeight: 120,
            maxHeight: 150,
          ),
          child: TextField(
            controller: jobDescriptionController,
            maxLines: null,
            expands: true,
            textAlignVertical: TextAlignVertical.top,
            style: AppTypography.bodySmall.copyWith(
              color: AppColors.cream,
              height: 1.4,
            ),
            decoration: InputDecoration(
              hintText: 'Paste job description or posting here...',
              hintStyle: AppTypography.bodySmall.copyWith(
                color: AppColors.textSecondary,
                fontSize: 11,
              ),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(6),
                borderSide: BorderSide(color: AppColors.dark2),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(6),
                borderSide: BorderSide(
                  color: AppColors.gold,
                  width: 2,
                ),
              ),
              filled: true,
              fillColor: AppColors.dark3,
              contentPadding: const EdgeInsets.all(12.0),
            ),
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Tailor Button
  // --------------------------------------------------------------------------
  Widget _buildTailorButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: isTailoring ? null : _tailorResume,
        icon: isTailoring
          ? SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(
                  AppColors.darkPrimary,
                ),
              ),
            )
          : const Icon(Icons.edit_outlined),
        label: Text(
          isTailoring ? 'Tailoring...' : 'Tailor Resume',
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.gold,
          foregroundColor: AppColors.darkPrimary,
          disabledBackgroundColor: AppColors.dark3,
          disabledForegroundColor: AppColors.textSecondary,
          padding: const EdgeInsets.symmetric(vertical: 12),
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Tailor Results
  // --------------------------------------------------------------------------
  Widget _buildTailorResults() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 24),
        Divider(
          height: 1,
          color: AppColors.dark2,
        ),
        const SizedBox(height: 16),
        // ======================================================
        // RESULTS HEADER: Keyword Matches
        // ======================================================
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
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        // ======================================================
        // RESULTS ITEMS: Match List
        // ======================================================
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: tailorMatches.length,
          itemBuilder: (context, index) => _buildTailorMatchItem(index),
        ),
        const SizedBox(height: 12),
        // ======================================================
        // BUTTON: Try Again
        // ======================================================
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _resetTailor,
            icon: const Icon(Icons.refresh_outlined),
            label: const Text('Try Again'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.dark2,
              foregroundColor: AppColors.cream,
              padding: const EdgeInsets.symmetric(vertical: 10),
            ),
          ),
        ),
        const SizedBox(height: 8),
        // ======================================================
        // BUTTON: Export as PDF
        // ======================================================
        SizedBox(
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
              padding: const EdgeInsets.symmetric(vertical: 10),
              disabledBackgroundColor: AppColors.successGreen.withOpacity(0.5),
              disabledForegroundColor: AppColors.darkPrimary.withOpacity(0.5),
            ),
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Single Tailor Match Item
  // --------------------------------------------------------------------------
  Widget _buildTailorMatchItem(int index) {
    final match = tailorMatches[index];
    final isHighRelevance =
        int.parse(match.relevance.replaceAll('%', '')) >= 90;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.dark3,
        border: Border.all(
          color: isHighRelevance
            ? AppColors.gold.withOpacity(0.3)
            : AppColors.dark2,
        ),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            match.category,
            style: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
              fontSize: 9,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  match.keyword,
                  style: AppTypography.labelText.copyWith(
                    color: AppColors.cream,
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: isHighRelevance
                    ? AppColors.successGreen.withOpacity(0.2)
                    : AppColors.dark2,
                  border: Border.all(
                    color: isHighRelevance
                      ? AppColors.successGreen
                      : Colors.transparent,
                  ),
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Text(
                  match.relevance,
                  style: AppTypography.bodySmall.copyWith(
                    color: isHighRelevance
                      ? AppColors.successGreen
                      : AppColors.textSecondary,
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: No Resumes Preview Panel (Right)
  // --------------------------------------------------------------------------
  Widget _buildNoResumesPreviewPanel() {
    return Center(
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
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Resume Preview Panel (Right)
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
                        ResumeFileService.getFileName(
                          resumeFiles[selectedResumeIndex].path,
                        ),
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.textSecondary,
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
                      resumeFiles[selectedResumeIndex],
                      pageLayoutMode: PdfPageLayoutMode.continuous,
                    ),
                    if (isTailoring) _buildTailoringOverlay(),
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
      color: hasTailored ? AppColors.gold : AppColors.textTertiary,
      tooltip: hasTailored
          ? 'Download tailored resume'
          : 'Tailor resume to download',
      onPressed: hasTailored
          ? () => _downloadTailoredResume()
          : null,
    );
  }

  // --------------------------------------------------------------------------
  // METHOD: Download Tailored Resume
  // --------------------------------------------------------------------------
  Future<void> _downloadTailoredResume() async {
    if (selectedResumeIndex >= resumeFiles.length) return;

    final sourceFile = resumeFiles[selectedResumeIndex];
    final originalFileName = ResumeFileService.getFileName(sourceFile.path);

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
              'tailored',
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
  // BUILD HELPER: Tailoring Overlay
  // --------------------------------------------------------------------------
  Widget _buildTailoringOverlay() {
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
              'Tailoring resume...',
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
