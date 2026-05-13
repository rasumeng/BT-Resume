/// Data models for Resume application
import 'package:json_annotation/json_annotation.dart';

part 'resume_model.g.dart';

/// Resume file metadata
@JsonSerializable()
class ResumeFile {
  final String name;
  final String path;
  final int size;
  final double modified;
  final double created;

  ResumeFile({
    required this.name,
    required this.path,
    required this.size,
    required this.modified,
    required this.created,
  });

  factory ResumeFile.fromJson(Map<String, dynamic> json) =>
      _$ResumeFileFromJson(json);
  Map<String, dynamic> toJson() => _$ResumeFileToJson(this);

  /// Get file extension
  String get extension => name.split('.').last.toLowerCase();

  /// Check if file is PDF
  bool get isPdf => extension == 'pdf';

  /// Check if file is text
  bool get isText => extension == 'txt' || extension == 'text';
}

/// Resume content wrapper
class ResumeContent {
  final String filename;
  final String content;
  final String? fullName;
  final String? email;
  final String? phone;
  final String? location;
  final String? summary;
  final List<String>? experience;
  final List<String>? skills;

  ResumeContent({
    required this.filename,
    required this.content,
    this.fullName,
    this.email,
    this.phone,
    this.location,
    this.summary,
    this.experience,
    this.skills,
  });
}

/// Polish request
class PolishRequest {
  final List<String> bullets;
  final String intensity; // 'light', 'medium', 'heavy'

  PolishRequest({required this.bullets, this.intensity = 'medium'});

  Map<String, dynamic> toJson() => {'bullets': bullets, 'intensity': intensity};
}

/// Polish response
@JsonSerializable()
class PolishResponse {
  final bool success;
  final List<String> bullets;
  final String? error;

  PolishResponse({required this.success, required this.bullets, this.error});

  factory PolishResponse.fromJson(Map<String, dynamic> json) =>
      _$PolishResponseFromJson(json);
  Map<String, dynamic> toJson() => _$PolishResponseToJson(this);
}

/// Grade data
@JsonSerializable()
class GradeData {
  final int score;
  final int? atsScore;
  final int? sectionsScore;
  final int? bulletsScore;
  final int? contentScore;
  final int? keywordsScore;
  final List<String>? strengths;
  final List<String>? improvements;
  final String? atsFeedback;

  GradeData({
    required this.score,
    this.atsScore,
    this.sectionsScore,
    this.bulletsScore,
    this.contentScore,
    this.keywordsScore,
    this.strengths,
    this.improvements,
    this.atsFeedback,
  });

  factory GradeData.fromJson(Map<String, dynamic> json) =>
      _$GradeDataFromJson(json);
  Map<String, dynamic> toJson() => _$GradeDataToJson(this);
}

/// Grade response
@JsonSerializable()
class GradeResponse {
  final bool success;
  final GradeData? grade;
  final String? error;

  GradeResponse({required this.success, this.grade, this.error});

  factory GradeResponse.fromJson(Map<String, dynamic> json) =>
      _$GradeResponseFromJson(json);
  Map<String, dynamic> toJson() => _$GradeResponseToJson(this);
}

/// Generic API response
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;
  final String timestamp;

  ApiResponse({
    required this.success,
    this.data,
    this.error,
    required this.timestamp,
  });
}
