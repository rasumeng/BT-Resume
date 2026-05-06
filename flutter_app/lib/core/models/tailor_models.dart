/// Models for job tailor feature
/// Contains TailorMatch, CategoryScore, and GapAnalysis data classes

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
}

class CategoryScore {
  final String category;
  final int score;

  CategoryScore({
    required this.category,
    required this.score,
  });
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
}
