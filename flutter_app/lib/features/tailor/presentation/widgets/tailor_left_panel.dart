import 'dart:io';

import 'package:flutter/material.dart';

import '../../../../config/colors.dart';
import '../../../../config/typography.dart';
import '../../../../core/services/resume_file_service.dart';
import '../../../../shared/widgets/custom_dropdown.dart';
import '../models/tailor_models.dart';

class TailorLeftPanel extends StatelessWidget {
  const TailorLeftPanel({
    super.key,
    required this.resumeFiles,
    required this.selectedResumeIndex,
    required this.isTailoring,
    required this.hasSeenFit,
    required this.userChoseToTailor,
    required this.hasTailored,
    required this.isGeneratingPdf,
    required this.tailorIntensity,
    required this.overallConfidence,
    required this.categoryScores,
    required this.tailorMatches,
    required this.tailorGaps,
    required this.jobPositionController,
    required this.jobCompanyController,
    required this.jobDescriptionController,
    required this.onResumeSelected,
    required this.onAnalyzeFit,
    required this.onEnableTailor,
    required this.onTailor,
    required this.onResetAnalysis,
    required this.onGeneratePdf,
    required this.onIntensityChanged,
  });

  final List<File> resumeFiles;
  final int selectedResumeIndex;
  final bool isTailoring;
  final bool hasSeenFit;
  final bool userChoseToTailor;
  final bool hasTailored;
  final bool isGeneratingPdf;
  final String tailorIntensity;
  final int overallConfidence;
  final List<CategoryScore> categoryScores;
  final List<TailorMatch> tailorMatches;
  final GapAnalysis? tailorGaps;

  final TextEditingController jobPositionController;
  final TextEditingController jobCompanyController;
  final TextEditingController jobDescriptionController;

  final ValueChanged<int> onResumeSelected;
  final VoidCallback onAnalyzeFit;
  final VoidCallback onEnableTailor;
  final VoidCallback onTailor;
  final VoidCallback onResetAnalysis;
  final VoidCallback onGeneratePdf;
  final ValueChanged<String> onIntensityChanged;

  @override
  Widget build(BuildContext context) {
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
          Container(
            height: 1,
            color: AppColors.gold.withOpacity(0.3),
          ),
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildResumeDropdown(),
                    const SizedBox(height: 16),
                    _buildJobInputFields(),
                    const SizedBox(height: 20),
                    if (!hasSeenFit)
                      _buildAnalyzeButton()
                    else ...[
                      _buildConfidenceGauge(),
                      const SizedBox(height: 16),
                      _buildCategoryScores(),
                      const SizedBox(height: 20),
                      if (!userChoseToTailor)
                        _buildDecisionButtons()
                      else ...[
                        _buildIntensityControl(),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: isTailoring ? null : onTailor,
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
                            itemBuilder: (context, index) => _buildTailorMatchItem(index),
                          ),
                          _buildGapAnalysis(),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: onResetAnalysis,
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
                              onPressed: isGeneratingPdf ? null : onGeneratePdf,
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
                              label: Text(
                                isGeneratingPdf ? 'Generating...' : 'Download Tailored Resume',
                              ),
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
        CustomResumeDropdown(
          resumeFiles: resumeFiles,
          selectedIndex: selectedResumeIndex,
          onChanged: onResumeSelected,
        ),
      ],
    );
  }

  Widget _buildJobInputFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
        Text(
          'Job Description *',
          style: AppTypography.bodySmall.copyWith(
            color: AppColors.cream,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          constraints: const BoxConstraints(
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
          child: Row(
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
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: isTailoring ? null : onAnalyzeFit,
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
            onPressed: isGeneratingPdf ? null : onGeneratePdf,
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
            label: Text(isGeneratingPdf ? 'Generating...' : 'Submit This Resume'),
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
            onPressed: onEnableTailor,
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
              SizedBox(
                width: 120,
                height: 120,
                child: CircularProgressIndicator(
                  value: overallConfidence / 100,
                  strokeWidth: 8,
                  backgroundColor: AppColors.dark3,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    overallConfidence >= 85
                        ? AppColors.successGreen
                        : overallConfidence >= 70
                            ? AppColors.gold
                            : AppColors.warningOrange,
                  ),
                ),
              ),
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
            overallConfidence >= 85
                ? 'Excellent fit!'
                : overallConfidence >= 70
                    ? 'Good match'
                    : 'Needs work',
            style: AppTypography.bodySmall.copyWith(
              color: overallConfidence >= 85
                  ? AppColors.successGreen
                  : overallConfidence >= 70
                      ? AppColors.gold
                      : AppColors.warningOrange,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

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
                score.score >= 85
                    ? AppColors.successGreen
                    : score.score >= 70
                        ? AppColors.gold
                        : AppColors.warningOrange,
              ),
            ),
          ),
        ],
      ),
    );
  }

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

  Widget _buildIntensityButton(String intensity, String label) {
    final isSelected = tailorIntensity == intensity;
    return GestureDetector(
      onTap: () => onIntensityChanged(intensity),
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

  Widget _buildTailorMatchItem(int index) {
    final match = tailorMatches[index];
    final isHighRelevance = int.parse(match.relevance.replaceAll('%', '')) >= 90;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.dark3,
        border: Border.all(
          color: isHighRelevance ? AppColors.gold.withOpacity(0.3) : AppColors.dark2,
        ),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
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
              color: isHighRelevance ? AppColors.successGreen.withOpacity(0.2) : AppColors.dark2,
              border: Border.all(
                color: isHighRelevance ? AppColors.successGreen : Colors.transparent,
              ),
              borderRadius: BorderRadius.circular(3),
            ),
            child: Text(
              match.relevance,
              style: AppTypography.bodySmall.copyWith(
                color: isHighRelevance ? AppColors.successGreen : AppColors.textSecondary,
                fontSize: 10,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
