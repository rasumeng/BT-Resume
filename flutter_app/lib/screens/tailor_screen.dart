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

class TailorScreen extends StatefulWidget {
  final List<ResumeFile> resumes;

  const TailorScreen({Key? key, required this.resumes}) : super(key: key);

  @override
  State<TailorScreen> createState() => _TailorScreenState();
}

class _TailorScreenState extends State<TailorScreen> {
  late ApiService _apiService;
  ResumeFile? selectedResume;
  ResumeContent? resumeContent;
  bool isLoading = false;
  final TextEditingController _jobDescriptionController =
      TextEditingController();
  String? tailoredResult;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService();
  }

  @override
  void dispose() {
    _jobDescriptionController.dispose();
    super.dispose();
  }

  Future<void> _loadResume(ResumeFile resume) async {
    setState(() {
      isLoading = true;
      selectedResume = resume;
      resumeContent = null;
      tailoredResult = null;
    });

    try {
      final content = await _apiService.getResume(resume.name);
      setState(() {
        resumeContent = content;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading resume: $e')),
        );
      }
    }
  }

  Future<void> _tailorResume() async {
    if (_jobDescriptionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a job description')),
      );
      return;
    }

    if (resumeContent == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a resume')),
      );
      return;
    }

    setState(() {
      isLoading = true;
      tailoredResult = null;
    });

    try {
      final resumeText = _formatResumeContent(resumeContent!);
      final response = await _apiService.tailorResume(
        resumeText,
        _jobDescriptionController.text,
      );

      setState(() {
        tailoredResult = response;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error tailoring resume: $e')),
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

  @override
  Widget build(BuildContext context) {
    return Container(
      color: btfDark,
      child: selectedResume == null
          ? _buildResumeSelector()
          : _buildTailorInterface(),
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
                child: const Icon(Icons.edit, color: btfGold, size: 20),
              ),
              const SizedBox(width: 16),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'TAILOR YOUR RESUME',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: btfGold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Customize for specific opportunities',
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
                      onTap: () => _loadResume(resume),
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

  Widget _buildTailorInterface() {
    return Column(
      children: [
        // Header with Back Button
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
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
                      'Customize for job posting',
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
        ),
        // Content
        Expanded(
          child: isLoading
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
                      // Input Section
                      const Text(
                        'JOB DESCRIPTION',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: btfGold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        decoration: BoxDecoration(
                          color: btfDark3,
                          border: Border.all(color: btfDark4),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: TextField(
                          controller: _jobDescriptionController,
                          maxLines: 10,
                          style: const TextStyle(color: btfCream, fontSize: 13),
                          cursorColor: btfGold,
                          decoration: InputDecoration(
                            hintText:
                                'Paste the job description here...\n\nThis will be used to tailor your resume to match the position requirements and highlight relevant keywords and skills.',
                            hintStyle: const TextStyle(color: btfDim, fontSize: 13),
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.all(16),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      // Tailor Button
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: Container(
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [btfGold, Color(0xFFd4b85f)],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Material(
                            color: Colors.transparent,
                            child: InkWell(
                              onTap: _tailorResume,
                              borderRadius: BorderRadius.circular(8),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: const [
                                  Icon(Icons.edit, color: btfDark, size: 18),
                                  SizedBox(width: 8),
                                  Text(
                                    'Tailor Resume',
                                    style: TextStyle(
                                      color: btfDark,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                      // Results
                      if (tailoredResult != null) ...[
                        const SizedBox(height: 32),
                        Container(
                          height: 1,
                          color: btfDark4,
                        ),
                        const SizedBox(height: 32),
                        const Text(
                          'TAILORED RESUME',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: btfGold,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: btfDark3,
                            border: Border.all(color: btfGold.withOpacity(0.3)),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: SelectableText(
                            tailoredResult!,
                            style: const TextStyle(
                              color: btfCream,
                              fontSize: 13,
                              height: 1.7,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          height: 44,
                          child: Container(
                            decoration: BoxDecoration(
                              border: Border.all(color: btfGold),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                onTap: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Copied to clipboard'),
                                      backgroundColor: btfGold,
                                    ),
                                  );
                                },
                                borderRadius: BorderRadius.circular(8),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: const [
                                    Icon(Icons.copy, color: btfGold, size: 18),
                                    SizedBox(width: 8),
                                    Text(
                                      'Copy Result',
                                      style: TextStyle(
                                        color: btfGold,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
        ),
      ],
    );
  }
}
