class TailorMatch {
  final String category;
  final String keyword;
  final String relevance;
  final String source;

  TailorMatch({
    required this.category,
    required this.keyword,
    required this.relevance,
    required this.source,
  });

  factory TailorMatch.fromApi(Map<String, dynamic> data) {
    return TailorMatch(
      category: data['category'] as String? ?? 'Keywords',
      keyword: data['keyword'] as String? ?? '',
      relevance: '${data['relevance'] as int? ?? 0}%',
      source: data['source'] as String? ?? 'Resume content',
    );
  }
}

class CategoryScore {
  final String category;
  final int score;

  CategoryScore({
    required this.category,
    required this.score,
  });

  factory CategoryScore.fromApi(Map<String, dynamic> data) {
    return CategoryScore(
      category: data['category'] as String? ?? 'Unknown',
      score: data['score'] as int? ?? 0,
    );
  }
}

class GapAnalysis {
  final List<String> missingSkills;
  final List<String> missingKeywords;
  final List<String> suggestions;

  GapAnalysis({
    required this.missingSkills,
    required this.missingKeywords,
    required this.suggestions,
  });

  factory GapAnalysis.fromApi(Map<String, dynamic> data) {
    return GapAnalysis(
      missingSkills: (data['missing_skills'] as List?)?.cast<String>() ?? [],
      missingKeywords: (data['missing_keywords'] as List?)?.cast<String>() ?? [],
      suggestions: (data['suggestions'] as List?)?.cast<String>() ?? [],
    );
  }
}

class TailorAnalysisResult {
  final int overallConfidence;
  final List<CategoryScore> categoryScores;
  final List<TailorMatch> matches;
  final GapAnalysis gaps;
  final String tailoredResume;
  final String changesSummary;

  const TailorAnalysisResult({
    required this.overallConfidence,
    required this.categoryScores,
    required this.matches,
    required this.gaps,
    this.tailoredResume = '',
    this.changesSummary = '',
  });

  factory TailorAnalysisResult.fromApi(Map<String, dynamic> data) {
    final categoryScores = (data['category_scores'] as List?)
            ?.map((e) => CategoryScore.fromApi(e as Map<String, dynamic>))
            .toList() ??
        [];

    final matches = (data['matches'] as List?)
            ?.map((e) => TailorMatch.fromApi(e as Map<String, dynamic>))
            .toList() ??
        [];

    return TailorAnalysisResult(
      overallConfidence: data['overall_confidence'] as int? ?? 0,
      categoryScores: categoryScores,
      matches: matches,
      gaps: GapAnalysis.fromApi(data['gaps'] as Map<String, dynamic>? ?? {}),
      tailoredResume: data['tailored_resume'] as String? ?? '',
      changesSummary: data['changes_summary'] as String? ?? 'Resume tailored to match job description.',
    );
  }
}
