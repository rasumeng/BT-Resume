// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resume_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ResumeFile _$ResumeFileFromJson(Map<String, dynamic> json) => ResumeFile(
  name: json['name'] as String,
  path: json['path'] as String,
  size: (json['size'] as num).toInt(),
  modified: (json['modified'] as num).toDouble(),
  created: (json['created'] as num).toDouble(),
);

Map<String, dynamic> _$ResumeFileToJson(ResumeFile instance) =>
    <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'size': instance.size,
      'modified': instance.modified,
      'created': instance.created,
    };

PolishResponse _$PolishResponseFromJson(Map<String, dynamic> json) =>
    PolishResponse(
      success: json['success'] as bool,
      bullets: (json['bullets'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      error: json['error'] as String?,
    );

Map<String, dynamic> _$PolishResponseToJson(PolishResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'bullets': instance.bullets,
      'error': instance.error,
    };

GradeData _$GradeDataFromJson(Map<String, dynamic> json) => GradeData(
  score: (json['score'] as num).toInt(),
  strengths: (json['strengths'] as List<dynamic>)
      .map((e) => e as String)
      .toList(),
  improvements: (json['improvements'] as List<dynamic>)
      .map((e) => e as String)
      .toList(),
  recommendations: (json['recommendations'] as List<dynamic>)
      .map((e) => e as String)
      .toList(),
);

Map<String, dynamic> _$GradeDataToJson(GradeData instance) => <String, dynamic>{
  'score': instance.score,
  'strengths': instance.strengths,
  'improvements': instance.improvements,
  'recommendations': instance.recommendations,
};

GradeResponse _$GradeResponseFromJson(Map<String, dynamic> json) =>
    GradeResponse(
      success: json['success'] as bool,
      grade: json['grade'] == null
          ? null
          : GradeData.fromJson(json['grade'] as Map<String, dynamic>),
      error: json['error'] as String?,
    );

Map<String, dynamic> _$GradeResponseToJson(GradeResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'grade': instance.grade,
      'error': instance.error,
    };
