/// Service for communicating with Flask backend
import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../constants/app_constants.dart';
import '../models/resume_model.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  late Dio _dio;
  final logger = Logger();

  factory ApiService() {
    return _instance;
  }

  ApiService._internal() {
    _initializeDio();
  }

  void _initializeDio() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.flaskApiBase,
        connectTimeout: Duration(
          milliseconds: AppConstants.connectionTimeout,
        ),
        receiveTimeout: Duration(
          milliseconds: AppConstants.receiveTimeout,
        ),
        contentType: 'application/json',
      ),
    );

    // Add logging interceptor
    _dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) => logger.i(obj),
      ),
    );
  }

  /// Check if backend is healthy and running
  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
      final data = response.data as Map<String, dynamic>;
      logger.i('✓ Backend health check passed');
      return data['status'] == 'healthy';
    } catch (e) {
      logger.w('✗ Backend health check failed: $e');
      return false;
    }
  }

  /// List all resumes
  Future<List<ResumeFile>> listResumes() async {
    try {
      final response = await _dio.get('/list-resumes');
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to list resumes');
      }

      final resumes = (data['resumes'] as List)
          .map((r) => ResumeFile.fromJson(r as Map<String, dynamic>))
          .toList();

      logger.i('✓ Listed ${resumes.length} resumes');
      return resumes;
    } catch (e) {
      logger.e('✗ Error listing resumes: $e');
      rethrow;
    }
  }

  /// Get resume content
  Future<ResumeContent> getResume(String filename) async {
    try {
      final response = await _dio.get(
        '/get-resume',
        queryParameters: {'filename': filename},
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to get resume');
      }

      logger.i('✓ Loaded resume: $filename');
      return ResumeContent(
        filename: filename,
        content: data['content'] as String,
      );
    } catch (e) {
      logger.e('✗ Error getting resume: $e');
      rethrow;
    }
  }

  /// Update resume content
  Future<void> updateResume(String filename, String content) async {
    try {
      final response = await _dio.post(
        '/update-resume',
        data: {
          'filename': filename,
          'content': content,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to update resume');
      }

      logger.i('✓ Updated resume: $filename');
    } catch (e) {
      logger.e('✗ Error updating resume: $e');
      rethrow;
    }
  }

  /// Delete resume
  Future<void> deleteResume(String filename) async {
    try {
      final response = await _dio.delete(
        '/delete-resume',
        queryParameters: {'filename': filename},
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to delete resume');
      }

      logger.i('✓ Deleted resume: $filename');
    } catch (e) {
      logger.e('✗ Error deleting resume: $e');
      rethrow;
    }
  }

  /// Polish resume bullets
  Future<List<String>> polishBullets(
    List<String> bullets, {
    String intensity = 'medium',
  }) async {
    try {
      final response = await _dio.post(
        '/polish-bullets',
        data: {
          'bullets': bullets,
          'intensity': intensity,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to polish bullets');
      }

      final polished = (data['bullets'] as List).cast<String>();
      logger.i('✓ Polished ${polished.length} bullets');
      return polished;
    } catch (e) {
      logger.e('✗ Error polishing bullets: $e');
      rethrow;
    }
  }

  /// Tailor resume to job description
  Future<String> tailorResume(
    String resumeText,
    String jobDescription,
  ) async {
    try {
      final response = await _dio.post(
        '/tailor-resume',
        data: {
          'resume_text': resumeText,
          'job_description': jobDescription,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to tailor resume');
      }

      logger.i('✓ Tailored resume');
      return data['tailored_resume'] as String;
    } catch (e) {
      logger.e('✗ Error tailoring resume: $e');
      rethrow;
    }
  }

  /// Grade resume
  Future<GradeData> gradeResume(String resumeText) async {
    try {
      final response = await _dio.post(
        '/grade-resume',
        data: {
          'resume_text': resumeText,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to grade resume');
      }

      final grade = GradeData.fromJson(data['grade'] as Map<String, dynamic>);
      logger.i('✓ Graded resume - Score: ${grade.score}');
      return grade;
    } catch (e) {
      logger.e('✗ Error grading resume: $e');
      rethrow;
    }
  }

  /// Parse resume to PDF format
  Future<Map<String, dynamic>> parseResume(String resumeText) async {
    try {
      final response = await _dio.post(
        '/parse-resume',
        data: {
          'resume_text': resumeText,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to parse resume');
      }

      logger.i('✓ Parsed resume');
      return data['parsed_resume'] as Map<String, dynamic>;
    } catch (e) {
      logger.e('✗ Error parsing resume: $e');
      rethrow;
    }
  }

  /// Save resume as PDF
  Future<String> savePdf(
    String filename,
    Map<String, dynamic> resumeData,
  ) async {
    try {
      final response = await _dio.post(
        '/save-resume-pdf',
        data: {
          'filename': filename,
          'resume_text': resumeData,
        },
      );
      final data = response.data as Map<String, dynamic>;

      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to save PDF');
      }

      logger.i('✓ Saved PDF: ${data['filename']}');
      return data['filename'] as String;
    } catch (e) {
      logger.e('✗ Error saving PDF: $e');
      rethrow;
    }
  }
}
