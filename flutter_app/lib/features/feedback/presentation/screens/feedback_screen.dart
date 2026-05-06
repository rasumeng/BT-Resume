import 'package:flutter/material.dart';
import '../../../../config/colors.dart';
import '../../../../config/typography.dart';
import '../../../../core/services/api_service.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({Key? key}) : super(key: key);

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  // Form state
  late TextEditingController _feedbackController;
  late TextEditingController _emailController;
  
  String _selectedType = 'general';
  int _selectedRating = 4;
  bool _isSubmitting = false;
  String? _successMessage;

  @override
  void initState() {
    super.initState();
    _feedbackController = TextEditingController();
    _emailController = TextEditingController();
  }

  @override
  void dispose() {
    _feedbackController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _submitFeedback() async {
    if (_feedbackController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter your feedback'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final result = await ApiService().submitFeedback(
        type: _selectedType,
        rating: _selectedRating,
        message: _feedbackController.text.trim(),
        email: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
      );

      if (result['success']) {
        setState(() {
          _successMessage = result['data']['message'];
          _feedbackController.clear();
          _emailController.clear();
          _selectedType = 'general';
          _selectedRating = 4;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_successMessage!),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );

        // Clear success message after 5 seconds
        await Future.delayed(const Duration(seconds: 5));
        if (mounted) {
          setState(() => _successMessage = null);
        }
      } else {
        throw Exception(result['error'] ?? 'Failed to submit feedback');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Text(
              'App Feedback',
              style: AppTypography.headingPageTitle.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Help us improve! Share your thoughts on the app, report bugs, or suggest new features.',
              style: AppTypography.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 48),

            // Feedback Type Selection
            Text(
              'Feedback Type',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildFeedbackTypeButton('General', 'general'),
                const SizedBox(width: 12),
                _buildFeedbackTypeButton('Feature Request', 'feature_request'),
                const SizedBox(width: 12),
                _buildFeedbackTypeButton('Bug Report', 'bug_report'),
              ],
            ),
            const SizedBox(height: 32),

            // App Rating
            Text(
              'How would you rate this app?',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 16),
            _buildStarRating(),
            const SizedBox(height: 32),

            // Feedback Message
            Text(
              'Your Feedback',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _feedbackController,
              maxLines: 6,
              enabled: !_isSubmitting,
              style: AppTypography.bodyLarge.copyWith(
                color: AppColors.cream,
              ),
              decoration: InputDecoration(
                hintText: 'Tell us what you think...',
                hintStyle: AppTypography.bodyLarge.copyWith(
                  color: AppColors.textSecondary,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: AppColors.gold.withOpacity(0.3),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: AppColors.gold,
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: AppColors.darkSecondary,
              ),
            ),
            const SizedBox(height: 24),

            // Optional Email
            Text(
              'Email (optional)',
              style: AppTypography.labelText.copyWith(
                color: AppColors.cream,
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _emailController,
              enabled: !_isSubmitting,
              style: AppTypography.bodyLarge.copyWith(
                color: AppColors.cream,
              ),
              decoration: InputDecoration(
                hintText: 'your@email.com (for follow-up)',
                hintStyle: AppTypography.bodyLarge.copyWith(
                  color: AppColors.textSecondary,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: AppColors.gold.withOpacity(0.3),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: AppColors.gold,
                    width: 2,
                  ),
                ),
                filled: true,
                fillColor: AppColors.darkSecondary,
              ),
            ),
            const SizedBox(height: 32),

            // Submit Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitFeedback,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.gold,
                  disabledBackgroundColor: AppColors.gold.withOpacity(0.5),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            AppColors.darkPrimary,
                          ),
                        ),
                      )
                    : Text(
                        'Submit Feedback',
                        style: AppTypography.labelText.copyWith(
                          color: AppColors.darkPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
              ),
            ),

            // Success Message
            if (_successMessage != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  border: Border.all(
                    color: Colors.green.withOpacity(0.3),
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle,
                      color: Colors.green,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: AppTypography.bodySmall.copyWith(
                          color: Colors.green,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 48),

            // Info Box
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.gold.withOpacity(0.05),
                border: Border.all(
                  color: AppColors.gold.withOpacity(0.2),
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '💡 Your feedback helps us improve!',
                    style: AppTypography.labelText.copyWith(
                      color: AppColors.gold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Whether it\'s a bug report, feature suggestion, or general feedback, we value your input. If you provide your email, we\'ll get back to you with updates!',
                    style: AppTypography.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeedbackTypeButton(String label, String value) {
    final isSelected = _selectedType == value;
    return Expanded(
      child: OutlinedButton(
        onPressed: _isSubmitting ? null : () {
          setState(() => _selectedType = value);
        },
        style: OutlinedButton.styleFrom(
          side: BorderSide(
            color: isSelected ? AppColors.gold : AppColors.gold.withOpacity(0.3),
            width: isSelected ? 2 : 1,
          ),
          backgroundColor: isSelected ? AppColors.gold.withOpacity(0.1) : Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: const EdgeInsets.symmetric(vertical: 12),
        ),
        child: Text(
          label,
          style: AppTypography.bodySmall.copyWith(
            color: isSelected ? AppColors.gold : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          ),
        ),
      ),
    );
  }

  Widget _buildStarRating() {
    return Row(
      children: List.generate(5, (index) {
        final isFilled = index < _selectedRating;
        return GestureDetector(
          onTap: _isSubmitting ? null : () {
            setState(() => _selectedRating = index + 1);
          },
          child: Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: Icon(
              isFilled ? Icons.star : Icons.star_border,
              color: AppColors.gold,
              size: 32,
            ),
          ),
        );
      }),
    );
  }
}