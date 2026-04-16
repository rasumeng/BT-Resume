import 'package:flutter/material.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({Key? key}) : super(key: key);

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resume Feedback',
            style: AppTypography.headingPageTitle.copyWith(
              color: AppColors.cream,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Get AI-powered feedback on your resume',
            style: AppTypography.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 48),
          
          Center(
            child: Column(
              children: [
                Icon(
                  Icons.assessment,
                  size: 64,
                  color: AppColors.gold,
                ),
                const SizedBox(height: 16),
                Text(
                  'Coming Soon',
                  style: AppTypography.headingPageTitle.copyWith(
                    color: AppColors.cream,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Feedback functionality is being built...',
                  style: AppTypography.bodyLarge.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}