import 'package:flutter/material.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';
import '../widgets/headers/panel_header.dart';
import '../widgets/states/empty_state.dart';
import '../widgets/buttons/primary_button.dart';
import '../widgets/buttons/secondary_button.dart';
import '../widgets/list_panel_item.dart';
import '../widgets/inputs/custom_input_field.dart';
import '../widgets/custom_scroll_bar.dart';

class TailorScreen extends StatefulWidget {
  const TailorScreen({Key? key}) : super(key: key);

  @override
  State<TailorScreen> createState() => _TailorScreenState();
}

class _TailorScreenState extends State<TailorScreen> {
  List<Map<String, String>> resumes = [
    {'name': 'Software Engineer - 2024', 'date': 'Updated 2 days ago'},
    {'name': 'Full Stack Developer', 'date': 'Updated 1 week ago'},
    {'name': 'Tech Lead Application', 'date': 'Updated 3 weeks ago'},
  ];

  int selectedResumeIndex = 0;
  late TextEditingController jobPositionController;
  late TextEditingController jobDescriptionController;

  String originalResume = '''John Doe
Senior Software Engineer

EXPERIENCE
Software Engineer at Tech Company (2022-Present)
- Led team of 5 developers on cloud migration project
- Improved system performance by 40% through optimization
- Architected microservices infrastructure using Kubernetes

Software Developer at StartUp Inc (2020-2022)
- Built full-stack web applications using React and Node.js
- Implemented CI/CD pipelines reducing deployment time by 60%

EDUCATION
B.S. Computer Science - State University (2020)

SKILLS
Languages: Python, JavaScript, Go, Java
Frameworks: React, Node.js, Django, Spring Boot''';

  String tailoredResume = '''John Doe
Senior Software Engineer | Cloud Architecture Specialist

PROFESSIONAL SUMMARY
Results-driven Senior Software Engineer with 5+ years of proven expertise in architecting scalable cloud solutions, leading high-performing development teams, and delivering mission-critical systems that drive business value. Seeking Principal Engineer role to leverage advanced architectural skills and mentorship experience.

CORE COMPETENCIES
• Cloud Architecture (AWS, Kubernetes, microservices)
• Team Leadership & Mentorship (5+ direct reports)
• System Design & Scalability (high-traffic applications)
• DevOps & CI/CD Pipeline Architecture
• Full-stack Development (React, Node.js, Python, Go)

EXPERIENCE
Senior Software Engineer at Tech Company (2022-Present)
• Led cloud migration initiative for enterprise infrastructure, architecting microservices infrastructure reducing operational costs by 30%
• Managed and mentored cross-functional team of 5 developers delivering mission-critical systems
• Designed and implemented Kubernetes infrastructure handling 100K+ concurrent users
• Optimized system architecture achieving 40% reduction in latency and 50% improvement in throughput

Senior Software Developer at StartUp Inc (2020-2022)
• Engineered full-stack web applications leveraging React and Node.js serving 500K+ active users
• Designed and deployed CI/CD pipelines using Docker and Kubernetes
• Established coding standards and best practices adopted across 20+ projects

TECHNICAL EXPERTISE
Languages: Python, JavaScript, Go, Java, TypeScript
Cloud & DevOps: AWS (EC2, S3, Lambda), GCP, Kubernetes, Docker, Terraform, Jenkins
Frameworks: React, Node.js, Django, Spring Boot, GraphQL
Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
Architecture: Microservices, Event-driven, Serverless

EDUCATION
B.S. Computer Science - State University (2020)''';

  @override
  void initState() {
    super.initState();
    jobPositionController = TextEditingController();
    jobDescriptionController = TextEditingController();
  }

  @override
  void dispose() {
    jobPositionController.dispose();
    jobDescriptionController.dispose();
    super.dispose();
  }

  void _selectResume(int index) {
    setState(() {
      selectedResumeIndex = index;
    });
  }

  void _tailorResume() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resume tailored successfully!'),
        backgroundColor: AppColors.successGreen,
      ),
    );
  }

  void _replaceOriginal() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Original resume replaced!'),
        backgroundColor: AppColors.successGreen,
      ),
    );
  }

  void _saveAs() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resume saved as new version!'),
        backgroundColor: AppColors.successGreen,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Left Panel (30%)
        Expanded(
          flex: 30,
          child: Container(
            color: AppColors.darkSecondary,
            child: Column(
              children: [
                PanelHeader(title: '📄 RESUMES'),
                Expanded(
                  child: resumes.isEmpty
                      ? EmptyState(
                          icon: Icons.description_outlined,
                          primaryMessage: 'No Resumes',
                          secondaryMessage: 'Upload a resume to tailor',
                          iconSize: 36,
                        )
                      : CustomScrollBar(
                          child: ListView.builder(
                            padding: const EdgeInsets.all(12),
                            itemCount: resumes.length,
                            itemBuilder: (context, index) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 8),
                                child: ListPanelItem(
                                  title: resumes[index]['name']!,
                                  subtitle: resumes[index]['date'],
                                  isSelected: selectedResumeIndex == index,
                                  onTap: () => _selectResume(index),
                                ),
                              );
                            },
                          ),
                        ),
                ),
                Container(
                  decoration: const BoxDecoration(
                    border: Border(
                      top: BorderSide(color: AppColors.dark4, width: 1),
                    ),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: CustomScrollBar(
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          CustomInputField(
                            label: 'Job Position',
                            placeholder: 'e.g., Principal Engineer',
                            controller: jobPositionController,
                          ),
                          const SizedBox(height: 16),
                          CustomInputField(
                            label: 'Job Description',
                            placeholder: 'Paste the full job posting...',
                            controller: jobDescriptionController,
                            maxLines: 6,
                          ),
                          const SizedBox(height: 16),
                          PrimaryButton(
                            label: '🎯 Tailor Resume',
                            onPressed: _tailorResume,
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
        // Right Panel (70%)
        Expanded(
          flex: 70,
          child: Container(
            color: AppColors.darkPrimary,
            child: Column(
              children: [
                // Top Section: Original vs Tailored (50/50)
                Expanded(
                  child: Row(
                    children: [
                      // Left Column - Original
                      Expanded(
                        child: Column(
                          children: [
                            PanelHeader(title: '📄 ORIGINAL RESUME'),
                            Expanded(
                              child: Container(
                                color: AppColors.dark2,
                                margin: const EdgeInsets.all(12),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(8),
                                  border:
                                      Border.all(color: AppColors.dark4, width: 1),
                                ),
                                child: CustomScrollBar(
                                  child: SingleChildScrollView(
                                    child: Text(
                                      originalResume,
                                      style: AppTypography.monospace,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      // Divider
                      Container(
                        width: 1,
                        color: AppColors.dark4,
                      ),
                      // Right Column - Tailored
                      Expanded(
                        child: Column(
                          children: [
                            PanelHeader(title: '🎯 TAILORED RESUME'),
                            Expanded(
                              child: Container(
                                color: AppColors.dark2,
                                margin: const EdgeInsets.all(12),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(8),
                                  border:
                                      Border.all(color: AppColors.dark4, width: 1),
                                ),
                                child: CustomScrollBar(
                                  child: SingleChildScrollView(
                                    child: Text(
                                      tailoredResume,
                                      style: AppTypography.monospace,
                                    ),
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
                // Bottom Section: Tailoring Summary & Actions
                Container(
                  decoration: const BoxDecoration(
                    border: Border(
                      top: BorderSide(color: AppColors.dark4, width: 1),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      PanelHeader(title: '📋 TAILORING SUMMARY'),
                      Container(
                        margin: const EdgeInsets.symmetric(horizontal: 12),
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Your resume has been tailored to match the job requirements with focus on:',
                              style: AppTypography.bodyNormal,
                            ),
                            const SizedBox(height: 12),
                            ...['Added professional summary aligned with role', 'Highlighted core competencies for the position', 'Reorganized experience emphasizing relevant skills', 'Added quantifiable metrics and achievements', 'Emphasized leadership and team collaboration']
                                .map((item) => Padding(
                                      padding: const EdgeInsets.only(bottom: 6),
                                      child: Row(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          const Icon(
                                            Icons.check_circle,
                                            color: AppColors.gold,
                                            size: 16,
                                          ),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(
                                              item,
                                              style:
                                                  AppTypography.bodySmall,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ))
                                .toList(),
                            const SizedBox(height: 16),
                            Row(
                              children: [
                                Expanded(
                                  child: PrimaryButton(
                                    label: '💾 Replace Original',
                                    onPressed: _replaceOriginal,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: SecondaryButton(
                                    label: '💾 Save As',
                                    onPressed: _saveAs,
                                  ),
                                ),
                              ],
                            ),
                          ],
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
