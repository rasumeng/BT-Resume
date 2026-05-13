import 'dart:io';

import '../../../../core/services/api_service.dart';
import '../../../../core/services/resume_file_service.dart';
import '../models/tailor_models.dart';

class TailorController {
  TailorController({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  final ApiService _apiService;

  Future<List<File>> loadResumeFiles() {
    return ResumeFileService.listResumeFiles();
  }

  Future<String> extractResumeText(File resumeFile) async {
    if (resumeFile.path.toLowerCase().endsWith('.pdf')) {
      return _apiService.extractPdfText(resumeFile);
    }
    return resumeFile.readAsString();
  }

  Future<TailorAnalysisResult> analyzeFit({
    required String resumeText,
    required String jobDescription,
  }) async {
    final analysisResult = await _apiService.analyzeFit(resumeText, jobDescription);
    return TailorAnalysisResult.fromApi(analysisResult);
  }

  Future<TailorAnalysisResult> tailorResume({
    required String resumeText,
    required String jobDescription,
    required String intensity,
  }) async {
    final tailorResult = await _apiService.tailorResume(
      resumeText,
      jobDescription,
      intensity: intensity,
    );
    return TailorAnalysisResult.fromApi(tailorResult);
  }

  Future<String> saveSamplePdf(String fileName) async {
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

    final pdfFilename = fileName.endsWith('.pdf') ? fileName : '$fileName.pdf';
    return _apiService.savePdf(pdfFilename, sampleResumeData);
  }

  Future<Map<String, dynamic>> saveTailoredTextPdf({
    required String filename,
    required String tailoredResumeText,
  }) {
    return _apiService.saveTextPdf(filename, tailoredResumeText);
  }
}
