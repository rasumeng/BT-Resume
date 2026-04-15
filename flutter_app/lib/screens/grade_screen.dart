import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/resume_model.dart';

// BTF Color Palette
const Color btfDark = Color(0xFF0D0D0B);
const Color btfDark2 = Color(0xFF1A1A17);
const Color btfDark3 = Color(0xFF252520);
const Color btfDark4 = Color(0xFF33332D);
const Color btfGold = Color(0xFFC9A84C);
const Color btfCream = Color(0xFFF5F0E8);
const Color btfMuted = Color(0xFFC4BFB3);
const Color btfDim = Color(0xFF8B8680);

class GradeScreen extends StatefulWidget {
  final List<ResumeFile> resumes;

  const GradeScreen({Key? key, required this.resumes}) : super(key: key);

  @override
  State<GradeScreen> createState() => _GradeScreenState();
}

class _GradeScreenState extends State<GradeScreen> {
  late ApiService _apiService;
  ResumeFile? selectedResume;
  ResumeContent? resumeContent;
  bool isLoading = false;
  GradeData? gradeResult;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService();
  }

  Future<void> _loadAndGradeResume(ResumeFile resume) async {
    setState(() {
      isLoading = true;
      selectedResume = resume;
      resumeContent = null;
      gradeResult = null;
    });

    try {
      final content = await _apiService.getResume(resume.name);
      setState(() {
        resumeContent = content;
      });

      // Grade the resume
      final grade = await _apiService.gradeResume(
        _formatResumeContent(content),
      );

      setState(() {
        gradeResult = grade;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error grading resume: $e')),
        );
      }
    }
  }

  String _formatResumeContent(ResumeContent content) {
    final buffer = StringBuffer();
    buffer.writeln(content.fullName ?? '');
    if (content.email != null) buffer.writeln(content.email);
    if (content.phone != null) buffer.writeln(content.phone);
    if (content.location != null) buffer.writeln(content.location);

    if (content.summary != null && content.summary!.isNotEmpty) {
      buffer.writeln('\nSummary:\n${content.summary}');
    }

    if (content.experience != null && content.experience!.isNotEmpty) {
      buffer.writeln('\nExperience:');
      for (var exp in content.experience!) {
        buffer.writeln(exp);
      }
    }

    if (content.skills != null && content.skills!.isNotEmpty) {
      buffer.writeln('\nSkills:\n${content.skills!.join(', ')}');
    }

    return buffer.toString();
  }

  Color _getGradeColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: btfDark,
      child: selectedResume == null
          ? _buildResumeSelector()
          : _buildGradeInterface(),
    );
  }

  Widget _buildResumeSelector() {
    if (widget.resumes.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: btfDark4,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.description, size: 32, color: btfGold),
            ),
            const SizedBox(height: 16),
            const Text(
              'No Resumes Available',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: btfCream,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Upload a resume to get started',
              style: TextStyle(
                fontSize: 14,
                color: btfMuted,
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Header
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [btfDark3, btfDark4],
            ),
            border: Border(bottom: BorderSide(color: btfDark4, width: 1)),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: btfGold.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.assessment, color: btfGold, size: 20),
              ),
              const SizedBox(width: 16),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'GRADE YOUR RESUME',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: btfGold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Get detailed feedback and scores',
                    style: TextStyle(
                      fontSize: 12,
                      color: btfDim,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        // Resume List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: widget.resumes.length,
            itemBuilder: (context, index) {
              final resume = widget.resumes[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Container(
                  decoration: BoxDecoration(
                    color: btfDark3,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: btfDark4),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [btfDark3, btfDark4.withOpacity(0.5)],
                    ),
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () => _loadAndGradeResume(resume),
                      borderRadius: BorderRadius.circular(8),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: btfGold.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Icon(
                                resume.isPdf ? Icons.picture_as_pdf : Icons.description,
                                color: btfGold,
                                size: 18,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    resume.name,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w600,
                                      color: btfCream,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '${(resume.size / 1024).toStringAsFixed(1)} KB',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: btfDim,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Icon(Icons.arrow_forward, color: btfGold, size: 18),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildGradeInterface() {
    return isLoading
        ? const Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(btfGold),
            ),
          )
        : SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Back Button Header
                Row(
                  children: [
                    Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () => setState(() => selectedResume = null),
                        borderRadius: BorderRadius.circular(6),
                        child: const Padding(
                          padding: EdgeInsets.all(8),
                          child: Icon(Icons.arrow_back, color: btfMuted, size: 20),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            selectedResume!.name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: btfGold,
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 2),
                          const Text(
                            'Resume Analysis',
                            style: TextStyle(
                              fontSize: 12,
                              color: btfDim,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                if (gradeResult != null) ...[
                  // Overall Score Circle
                  Center(
                    child: SizedBox(
                      width: 160,
                      height: 160,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Container(
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  btfDark3,
                                  btfDark4,
                                ],
                              ),
                              border: Border.all(
                                color: btfGold,
                                width: 2,
                              ),
                            ),
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                gradeResult!.score.toString(),
                                style: const TextStyle(
                                  fontSize: 56,
                                  fontWeight: FontWeight.bold,
                                  color: btfGold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              const Text(
                                'Overall',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: btfDim,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                  // Strengths
                  const Text(
                    'STRENGTHS',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: btfGold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ..._buildFeedbackList(gradeResult!.strengths, Colors.green),
                  const SizedBox(height: 28),
                  // Areas for Improvement
                  const Text(
                    'AREAS FOR IMPROVEMENT',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: btfGold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ..._buildFeedbackList(gradeResult!.improvements, Colors.orange),
                  const SizedBox(height: 28),
                  // Recommendations
                  const Text(
                    'RECOMMENDATIONS',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: btfGold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ..._buildRecommendationList(gradeResult!.recommendations),
                ] else
                  const Center(
                    child: Text(
                      'Unable to grade resume',
                      style: TextStyle(color: btfMuted),
                    ),
                  ),
              ],
            ),
          );
  }

  List<Widget> _buildFeedbackList(List<String> items, Color iconColor) {
    return items
        .asMap()
        .entries
        .map(
          (entry) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: btfDark3,
                    border: Border.all(color: iconColor),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    entry.key == 0 ? Icons.check_circle : Icons.lightbulb,
                    color: iconColor,
                    size: 16,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    entry.value,
                    style: const TextStyle(
                      fontSize: 13,
                      color: btfCream,
                      height: 1.6,
                    ),
                  ),
                ),
              ],
            ),
          ),
        )
        .toList();
  }

  List<Widget> _buildRecommendationList(List<String> items) {
    return items
        .asMap()
        .entries
        .map(
          (entry) => Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Container(
              decoration: BoxDecoration(
                color: btfDark3,
                border: Border.all(color: btfDark4),
                borderRadius: BorderRadius.circular(8),
              ),
              padding: const EdgeInsets.all(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 28,
                    height: 28,
                    decoration: const BoxDecoration(
                      color: btfGold,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${entry.key + 1}',
                        style: const TextStyle(
                          color: btfDark,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      entry.value,
                      style: const TextStyle(
                        fontSize: 13,
                        color: btfCream,
                        height: 1.6,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        )
        .toList();
  }
}
