import 'package:flutter/material.dart';
import 'dart:io';
import 'package:path/path.dart' as p;
import 'package:syncfusion_flutter_pdfviewer/pdfviewer.dart';
import '../../../../config/colors.dart';
import '../../../../config/typography.dart';
import '../../../../core/services/resume_file_service.dart';
import '../../../../core/services/api_service.dart';
import '../../../../shared/widgets/download_dialog.dart';

// ============================================================================
// TailorMatch Model
// ============================================================================
class TailorMatch {
  /* MEMBERS */
  final String category;
  final String keyword;
  final String relevance;
  final String source;

  /* CONSTRUCTOR */
  TailorMatch({
    required this.category,
    required this.keyword,
    required this.relevance,
    required this.source,
  });
}

// ============================================================================
// CategoryScore Model
// ============================================================================
class CategoryScore {
  /* MEMBERS */
  final String category;
  final int score;

  /* CONSTRUCTOR */
  CategoryScore({
    required this.category,
    required this.score,
  });
}

// ============================================================================
// GapAnalysis Model
// ============================================================================
class GapAnalysis {
  /* MEMBERS */
  final List<String> missingSkills;
  final List<String> missingKeywords;
  final List<String> suggestions;

  /* CONSTRUCTOR */
  GapAnalysis({
    required this.missingSkills,
    required this.missingKeywords,
    required this.suggestions,
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
  bool showBeforeTailorPreview = false;
  bool hasSeenFit = false;
  bool userChoseToTailor = false;
  String tailorIntensity = 'medium'; // 'light' | 'medium' | 'heavy'
  int overallConfidence = 0;
  List<CategoryScore> categoryScores = [];
  List<TailorMatch> tailorMatches = [];
  GapAnalysis? tailorGaps;
  String changesSummary = '';
  String originalResumeText = '';
  String tailoredResumeText = '';
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

    if (resumeFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('No resume selected'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    try {
      setState(() {
        isTailoring = true;
      });

      // Get the selected resume file
      final resumeFile = resumeFiles[selectedResumeIndex];
      final fileName = p.basename(resumeFile.path);
      print('📋 Starting tailor for: $fileName');

      // Extract text from resume
      String resumeText;
      if (resumeFile.path.toLowerCase().endsWith('.pdf')) {
        print('🔍 Extracting text from PDF...');
        resumeText = await _apiService.extractPdfText(resumeFile);
      } else {
        print('📄 Reading text file...');
        resumeText = await resumeFile.readAsString();
      }

      setState(() {
        originalResumeText = resumeText;
      });

      if (resumeText.isEmpty) {
        throw Exception('Resume text is empty');
      }

      print('✓ Extracted ${resumeText.length} characters from resume');
      print('🚀 Calling tailor API with LLM analysis...');

      // Call the tailor API with LLM analysis
      final tailorResult = await _apiService.tailorResume(
        resumeText,
        jobDescriptionController.text,
        intensity: tailorIntensity,
      );

      print('✓ Received tailored resume with analysis: ${tailorResult['tailored_resume'].length} characters');

      // Parse the analysis data from the backend
      final overallConfidenceValue = tailorResult['overall_confidence'] as int? ?? 0;
      final categoryScoresList = (tailorResult['category_scores'] as List?)?.map((e) {
        final scoreMap = e as Map<String, dynamic>;
        return CategoryScore(
          category: scoreMap['category'] as String? ?? 'Unknown',
          score: scoreMap['score'] as int? ?? 0,
        );
      }).toList() ?? [];
      
      final matchesList = (tailorResult['matches'] as List?)?.map((e) {
        final matchMap = e as Map<String, dynamic>;
        return TailorMatch(
          category: matchMap['category'] as String? ?? 'Keywords',
          keyword: matchMap['keyword'] as String? ?? '',
          relevance: '${matchMap['relevance'] as int? ?? 0}%',
          source: matchMap['source'] as String? ?? 'Resume content',
        );
      }).toList() ?? [];
      
      final gapsData = tailorResult['gaps'] as Map<String, dynamic>? ?? {};
      final gapAnalysis = GapAnalysis(
        missingSkills: (gapsData['missing_skills'] as List?)?.cast<String>() ?? [],
        missingKeywords: (gapsData['missing_keywords'] as List?)?.cast<String>() ?? [],
        suggestions: (gapsData['suggestions'] as List?)?.cast<String>() ?? [],
      );

      setState(() {
        hasTailored = true;
        isTailoring = false;
        tailoredResumeText = tailorResult['tailored_resume'] as String? ?? '';
        overallConfidence = overallConfidenceValue;
        categoryScores = categoryScoresList;
        tailorMatches = matchesList;
        tailorGaps = gapAnalysis;
        changesSummary = tailorResult['changes_summary'] as String? ?? 'Resume tailored to match job description.';
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('✓ Resume tailored successfully!'),
            backgroundColor: AppColors.successGreen,
          ),
        );
      }
    } catch (e) {
      print('✗ Error tailoring resume: $e');
      setState(() {
        isTailoring = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error tailoring resume: $e'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Reset Analysis (Back to empty state)
  // --------------------------------------------------------------------------
  void _resetAnalysis() {
    setState(() {
      hasSeenFit = false;
      userChoseToTailor = false;
      hasTailored = false;
      tailorMatches = [];
      categoryScores = [];
      tailorGaps = null;
      overallConfidence = 0;
      changesSummary = '';
      showBeforeTailorPreview = false;
      jobPositionController.clear();
      jobCompanyController.clear();
      jobDescriptionController.clear();
    });
  }

  // --------------------------------------------------------------------------
  // METHOD: Analyze Fit (Show confidence without tailoring)
  // --------------------------------------------------------------------------
  Future<void> _analyzeFit() async {
    if (jobDescriptionController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Please enter a job description'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    if (resumeFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('No resume selected'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    try {
      setState(() {
        isTailoring = true;
      });

      // Get the selected resume file
      final resumeFile = resumeFiles[selectedResumeIndex];
      final fileName = p.basename(resumeFile.path);
      print('📋 Starting fit analysis for: $fileName');

      // Extract text from resume
      String resumeText;
      if (resumeFile.path.toLowerCase().endsWith('.pdf')) {
        print('🔍 Extracting text from PDF...');
        resumeText = await _apiService.extractPdfText(resumeFile);
      } else {
        print('📄 Reading text file...');
        resumeText = await resumeFile.readAsString();
      }

      if (resumeText.isEmpty) {
        throw Exception('Resume text is empty');
      }

      print('✓ Extracted ${resumeText.length} characters from resume');
      print('🚀 Calling fit analysis API with LLM...');

      // Call the fit analysis API with LLM
      final analysisResult = await _apiService.analyzeFit(
        resumeText,
        jobDescriptionController.text,
      );

      print('✓ Received fit analysis: ${analysisResult['overall_confidence']}% confidence');

      // Parse the analysis data from the backend
      final overallConfidenceValue = analysisResult['overall_confidence'] as int? ?? 0;
      final categoryScoresList = (analysisResult['category_scores'] as List?)?.map((e) {
        final scoreMap = e as Map<String, dynamic>;
        return CategoryScore(
          category: scoreMap['category'] as String? ?? 'Unknown',
          score: scoreMap['score'] as int? ?? 0,
        );
      }).toList() ?? [];
      
      final matchesList = (analysisResult['matches'] as List?)?.map((e) {
        final matchMap = e as Map<String, dynamic>;
        return TailorMatch(
          category: matchMap['category'] as String? ?? 'Keywords',
          keyword: matchMap['keyword'] as String? ?? '',
          relevance: '${matchMap['relevance'] as int? ?? 0}%',
          source: matchMap['source'] as String? ?? 'Resume content',
        );
      }).toList() ?? [];
      
      final gapsData = analysisResult['gaps'] as Map<String, dynamic>? ?? {};
      final gapAnalysis = GapAnalysis(
        missingSkills: (gapsData['missing_skills'] as List?)?.cast<String>() ?? [],
        missingKeywords: (gapsData['missing_keywords'] as List?)?.cast<String>() ?? [],
        suggestions: (gapsData['suggestions'] as List?)?.cast<String>() ?? [],
      );

      setState(() {
        hasSeenFit = true;
        isTailoring = false;
        userChoseToTailor = false;
        overallConfidence = overallConfidenceValue;
        categoryScores = categoryScoresList;
        tailorMatches = matchesList;
        tailorGaps = gapAnalysis;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Analysis complete! See your fit above.'),
            backgroundColor: AppColors.successGreen,
          ),
        );
      }
    } catch (e) {
      print('✗ Error analyzing fit: $e');
      setState(() {
        isTailoring = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error analyzing fit: $e'),
            backgroundColor: AppColors.errorRed,
          ),
        );
      }
    }
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
  // BUILD HELPER: Left Panel Content (UNIFIED SECTION)
  // --------------------------------------------------------------------------
  Widget _buildLeftPanelContent() {
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
          // ==============================================================
          // HEADER
          // ==============================================================
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Job Tailor',
                  style: AppTypography.labelText.copyWith(
                    color: AppColors.cream,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Select a resume and enter a job description to see your fit',
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          // ==============================================================
          // DIVIDER
          // ==============================================================
          Container(
            height: 1,
            color: AppColors.gold.withOpacity(0.3),
          ),
          // ==============================================================
          // CONTENT: Scrollable form
          // ==============================================================
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ======================================================
                    // 1. RESUME SELECTOR (Dropdown)
                    // ======================================================
                    _buildResumeDropdown(),
                    const SizedBox(height: 16),
                    // ======================================================
                    // 2. JOB DETAILS INPUTS
                    // ======================================================
                    _buildJobInputFields(),
                    const SizedBox(height: 20),
                    // ======================================================
                    // 3. MATCH BREAKDOWN (Empty until user analyzes)
                    // ======================================================
                    if (!hasSeenFit)
                      _buildAnalyzeButton()
                    else ...[
                      _buildConfidenceGauge(),
                      const SizedBox(height: 16),
                      _buildCategoryScores(),
                      const SizedBox(height: 20),
                      // ======================================================
                      // 4. DECISION BUTTONS (Submit or Tailor)
                      // ======================================================
                      if (!userChoseToTailor)
                        _buildDecisionButtons()
                      else ...[
                        // ======================================================
                        // 5. INTENSITY CONTROL (if tailoring)
                        // ======================================================
                        _buildIntensityControl(),
                        const SizedBox(height: 16),
                        // ======================================================
                        // TAILOR BUTTON
                        // ======================================================
                        SizedBox(
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
                              isTailoring ? 'Tailoring...' : 'Generate Tailored Resume',
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.gold,
                              foregroundColor: AppColors.darkPrimary,
                              disabledBackgroundColor: AppColors.dark3,
                              disabledForegroundColor: AppColors.textSecondary,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        // ======================================================
                        // RESULTS SECTION (if tailored)
                        // ======================================================
                        if (hasTailored) ...[
                          Divider(height: 1, color: AppColors.dark2),
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
                                'Top Matches',
                                style: AppTypography.labelText.copyWith(
                                  color: AppColors.cream,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: tailorMatches.length,
                            itemBuilder: (context, index) =>
                                _buildTailorMatchItem(index),
                          ),
                          _buildGapAnalysis(),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: _resetAnalysis,
                              icon: const Icon(Icons.refresh_outlined),
                              label: const Text('Try Different Job'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.dark2,
                                foregroundColor: AppColors.cream,
                                padding: const EdgeInsets.symmetric(vertical: 10),
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
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
                                        valueColor:
                                            AlwaysStoppedAnimation<Color>(
                                          AppColors.darkPrimary
                                              .withOpacity(0.7),
                                        ),
                                      ),
                                    )
                                  : const Icon(Icons.download),
                              label: Text(isGeneratingPdf
                                  ? 'Generating...'
                                  : 'Download Tailored Resume'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.successGreen,
                                foregroundColor: AppColors.darkPrimary,
                                padding: const EdgeInsets.symmetric(vertical: 10),
                                disabledBackgroundColor:
                                    AppColors.successGreen.withOpacity(0.5),
                                disabledForegroundColor:
                                    AppColors.darkPrimary.withOpacity(0.5),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ],
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
  // BUILD HELPER: Resume Dropdown Selector
  // --------------------------------------------------------------------------
  Widget _buildResumeDropdown() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select Resume *',
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.cream,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: AppColors.dark3),
            borderRadius: BorderRadius.circular(6),
          ),
          child: DropdownButton<int>(
            value: selectedResumeIndex,
            onChanged: (int? newValue) {
              if (newValue != null) {
                setState(() {
                  selectedResumeIndex = newValue;
                  _resetAnalysis();
                });
              }
            },
            isExpanded: true,
            underline: const SizedBox(),
            dropdownColor: AppColors.dark2,
            style: AppTypography.bodySmall.copyWith(
              color: AppColors.cream,
            ),
            items: resumeFiles.asMap().entries.map((entry) {
              final index = entry.key;
              final file = entry.value;
              final fileName =
                  ResumeFileService.getFileName(file.path);
              return DropdownMenuItem<int>(
                value: index,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Row(
                    children: [
                      Icon(
                        Icons.picture_as_pdf,
                        color: AppColors.errorRed,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          fileName,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Analyze Button (Before seeing fit)
  // --------------------------------------------------------------------------
  Widget _buildAnalyzeButton() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.dark3,
            border: Border.all(color: AppColors.dark2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: AppColors.gold,
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Fill in the job details and analyze to see your fit',
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: isTailoring ? null : _analyzeFit,
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
                : const Icon(Icons.analytics_outlined),
            label: Text(
              isTailoring ? 'Analyzing...' : 'See How I Fit',
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.gold,
              foregroundColor: AppColors.darkPrimary,
              disabledBackgroundColor: AppColors.dark3,
              disabledForegroundColor: AppColors.textSecondary,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Decision Buttons (After seeing fit)
  // --------------------------------------------------------------------------
  Widget _buildDecisionButtons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'What would you like to do?',
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 12),
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
            label: Text(isGeneratingPdf
                ? 'Generating...'
                : 'Submit This Resume'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.successGreen,
              foregroundColor: AppColors.darkPrimary,
              padding: const EdgeInsets.symmetric(vertical: 12),
              disabledBackgroundColor: AppColors.successGreen.withOpacity(0.5),
              disabledForegroundColor: AppColors.darkPrimary.withOpacity(0.5),
            ),
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {
              setState(() {
                userChoseToTailor = true;
                tailorIntensity = 'medium';
              });
            },
            icon: const Icon(Icons.tune),
            label: const Text('Tailor Resume'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.dark2,
              foregroundColor: AppColors.cream,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }


  Widget _buildConfidenceGauge() {
    return Center(
      child: Column(
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              // Background circle
              SizedBox(
                width: 120,
                height: 120,
                child: CircularProgressIndicator(
                  value: overallConfidence / 100,
                  strokeWidth: 8,
                  backgroundColor: AppColors.dark3,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    overallConfidence >= 85 ? AppColors.successGreen :
                    overallConfidence >= 70 ? AppColors.gold :
                    AppColors.warningOrange
                  ),
                ),
              ),
              // Center text
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    '$overallConfidence%',
                    style: AppTypography.scoreDisplay.copyWith(
                      color: AppColors.gold,
                      fontSize: 28,
                    ),
                  ),
                  Text(
                    'Match',
                    style: AppTypography.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            overallConfidence >= 85 ? 'Excellent fit!' :
            overallConfidence >= 70 ? 'Good match' :
            'Needs work',
            style: AppTypography.bodySmall.copyWith(
              color: overallConfidence >= 85 ? AppColors.successGreen :
              overallConfidence >= 70 ? AppColors.gold :
              AppColors.warningOrange,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Category Scores Breakdown
  // --------------------------------------------------------------------------
  Widget _buildCategoryScores() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Match Breakdown',
          style: AppTypography.labelText.copyWith(
            color: AppColors.cream,
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        ...categoryScores.map((score) => _buildCategoryScoreItem(score)),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Single Category Score Item
  // --------------------------------------------------------------------------
  Widget _buildCategoryScoreItem(CategoryScore score) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                score.category,
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.cream,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${score.score}%',
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.gold,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score.score / 100,
              minHeight: 6,
              backgroundColor: AppColors.dark3,
              valueColor: AlwaysStoppedAnimation<Color>(
                score.score >= 85 ? AppColors.successGreen :
                score.score >= 70 ? AppColors.gold :
                AppColors.warningOrange
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Intensity Control
  // --------------------------------------------------------------------------
  Widget _buildIntensityControl() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Tailor Intensity',
          style: AppTypography.labelText.copyWith(
            color: AppColors.cream,
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildIntensityButton('light', 'Light'),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildIntensityButton('medium', 'Medium'),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildIntensityButton('heavy', 'Heavy'),
            ),
          ],
        ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Single Intensity Button
  // --------------------------------------------------------------------------
  Widget _buildIntensityButton(String intensity, String label) {
    final isSelected = tailorIntensity == intensity;
    return GestureDetector(
      onTap: () {
        setState(() {
          tailorIntensity = intensity;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.dark3 : AppColors.dark2,
          border: Border.all(
            color: isSelected ? AppColors.gold : AppColors.dark3,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: AppTypography.bodySmall.copyWith(
            color: isSelected ? AppColors.gold : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
            fontSize: 11,
          ),
        ),
      ),
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Gap Analysis Section
  // --------------------------------------------------------------------------
  Widget _buildGapAnalysis() {
    if (tailorGaps == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 16),
        Divider(height: 1, color: AppColors.dark2),
        const SizedBox(height: 16),
        Row(
          children: [
            Icon(
              Icons.lightbulb_outline,
              color: AppColors.warningOrange,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              'Opportunities to Improve',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        // Missing Skills
        if (tailorGaps!.missingSkills.isNotEmpty)
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Missing Skills',
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                  fontSize: 11,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: tailorGaps!.missingSkills.map((skill) {
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.warningOrange.withOpacity(0.1),
                      border: Border.all(
                        color: AppColors.warningOrange.withOpacity(0.3),
                      ),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      skill,
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.warningOrange,
                        fontSize: 10,
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
            ],
          ),
        // Suggestions
        if (tailorGaps!.suggestions.isNotEmpty)
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Suggestions',
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                  fontSize: 11,
                ),
              ),
              const SizedBox(height: 8),
              ...tailorGaps!.suggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '•',
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.gold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          suggestion,
                          style: AppTypography.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                            fontSize: 10,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],
          ),
      ],
    );
  }

  // --------------------------------------------------------------------------
  // BUILD HELPER: Before/After Toggle
  // --------------------------------------------------------------------------
  Widget _buildBeforeAfterToggle() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Preview',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            Container(
              decoration: BoxDecoration(
                color: AppColors.dark2,
                borderRadius: BorderRadius.circular(20),
              ),
              padding: const EdgeInsets.all(2),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        showBeforeTailorPreview = false;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: !showBeforeTailorPreview ? AppColors.dark3 : Colors.transparent,
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Text(
                        'After',
                        style: AppTypography.bodySmall.copyWith(
                          color: !showBeforeTailorPreview ? AppColors.gold : AppColors.textSecondary,
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        showBeforeTailorPreview = true;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: showBeforeTailorPreview ? AppColors.dark3 : Colors.transparent,
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Text(
                        'Before',
                        style: AppTypography.bodySmall.copyWith(
                          color: showBeforeTailorPreview ? AppColors.gold : AppColors.textSecondary,
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.dark3,
            border: Border.all(color: AppColors.dark2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (showBeforeTailorPreview)
                Text(
                  '[Original Resume - no modifications]',
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontStyle: FontStyle.italic,
                    height: 1.5,
                  ),
                )
              else
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.gold.withOpacity(0.1),
                        border: Border.all(
                          color: AppColors.gold.withOpacity(0.3),
                        ),
                        borderRadius: BorderRadius.circular(3),
                      ),
                      child: Text(
                        'TAILORED',
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.gold,
                          fontSize: 8,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      changesSummary,
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.cream,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ],
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
        const SizedBox(height: 20),
        // ======================================================
        // CONFIDENCE GAUGE
        // ======================================================
        _buildConfidenceGauge(),
        const SizedBox(height: 24),
        // ======================================================
        // CATEGORY SCORES
        // ======================================================
        _buildCategoryScores(),
        const SizedBox(height: 24),
        // ======================================================
        // INTENSITY CONTROL
        // ======================================================
        _buildIntensityControl(),
        const SizedBox(height: 24),
        // ======================================================
        // MATCHED KEYWORDS
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
              'Top Matches',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: tailorMatches.length,
          itemBuilder: (context, index) => _buildTailorMatchItem(index),
        ),
        // ======================================================
        // GAP ANALYSIS
        // ======================================================
        _buildGapAnalysis(),
        const SizedBox(height: 24),
        // ======================================================
        // BEFORE/AFTER TOGGLE
        // ======================================================
        _buildBeforeAfterToggle(),
        const SizedBox(height: 20),
        // ======================================================
        // BUTTONS
        // ======================================================
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _resetAnalysis,
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      match.keyword,
                      style: AppTypography.labelText.copyWith(
                        color: AppColors.cream,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      match.source,
                      style: AppTypography.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: 9,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
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
                    fontSize: 10,
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
    if (tailoredResumeText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No tailored resume to download'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    if (selectedResumeIndex >= resumeFiles.length) return;

    final sourceFile = resumeFiles[selectedResumeIndex];
    final originalFileName = ResumeFileService.getFileName(sourceFile.path);

    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => DownloadDialog(
          originalFileName: originalFileName,
          onDownload: (fileName, replaceOriginal) async {
            await _performDownloadTailored(
              fileName,
              replaceOriginal,
            );
          },
        ),
      );
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Perform Tailored Download
  // --------------------------------------------------------------------------
  Future<void> _performDownloadTailored(
    String fileName,
    bool replaceOriginal,
  ) async {
    try {
      setState(() {
        isGeneratingPdf = true;
      });

      // Ensure filename ends with .pdf
      final pdfFilename =
          fileName.endsWith('.pdf') ? fileName : '$fileName.pdf';

      print('💾 Saving tailored resume as: $pdfFilename');

      // Call API to save as text PDF
      final result = await _apiService.saveTextPdf(pdfFilename, tailoredResumeText);

      if (mounted) {
        setState(() {
          isGeneratingPdf = false;
        });

        if (result['success'] == true) {
          final message = replaceOriginal
              ? '✓ Resume replaced: $pdfFilename'
              : '✓ Tailored resume saved: $pdfFilename';

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: AppColors.successGreen,
              duration: const Duration(seconds: 3),
            ),
          );
        } else {
          throw Exception(
              result['error'] ?? 'Failed to save tailored resume');
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          isGeneratingPdf = false;
        });

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
