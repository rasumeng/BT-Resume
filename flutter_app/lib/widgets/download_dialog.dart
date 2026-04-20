import 'package:flutter/material.dart';
import '../constants/colors.dart';
import '../constants/typography.dart';

class DownloadOption {
  final String label;
  final String subtitle;

  DownloadOption({required this.label, required this.subtitle});
}

class DownloadDialog extends StatefulWidget {
  final String originalFileName;
  final Function(String fileName, bool replaceOriginal) onDownload;

  const DownloadDialog({
    Key? key,
    required this.originalFileName,
    required this.onDownload,
  }) : super(key: key);

  @override
  State<DownloadDialog> createState() => _DownloadDialogState();
}

class _DownloadDialogState extends State<DownloadDialog> {
  late TextEditingController _fileNameController;
  int _selectedOption = 0; // 0 = custom name, 1 = replace original

  @override
  void initState() {
    super.initState();
    _fileNameController = TextEditingController(
      text: widget.originalFileName.replaceAll('.pdf', ''),
    );
  }

  @override
  void dispose() {
    _fileNameController.dispose();
    super.dispose();
  }

  void _handleDownload() {
    final fileName = _fileNameController.text.trim();
    if (fileName.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a filename'),
          backgroundColor: AppColors.errorRed,
        ),
      );
      return;
    }

    Navigator.of(context).pop();
    widget.onDownload(fileName, _selectedOption == 1);
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.darkSecondary,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: AppColors.gold.withOpacity(0.3),
        ),
      ),
      child: SingleChildScrollView(
        child: Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                'Download Resume',
                style: AppTypography.headingPageTitle.copyWith(
                  color: AppColors.cream,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Default location: Documents > Resume AI > resumes',
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.gold,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 24),

              // Option 1: Custom Name
              _buildOption(
                index: 0,
                label: 'Save with custom name',
                subtitle: 'Choose a new filename',
              ),
              if (_selectedOption == 0) ...[
                const SizedBox(height: 12),
                TextField(
                  controller: _fileNameController,
                  style: AppTypography.bodyLarge.copyWith(
                    color: AppColors.cream,
                  ),
                  decoration: InputDecoration(
                    hintText: 'Enter filename (without .pdf)',
                    hintStyle: AppTypography.bodySmall.copyWith(
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
                    fillColor: AppColors.darkPrimary,
                    suffixText: '.pdf',
                    suffixStyle: AppTypography.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              const SizedBox(height: 12),

              // Option 2: Replace Original
              _buildOption(
                index: 1,
                label: 'Replace original file',
                subtitle: 'Overwrite ${widget.originalFileName}',
              ),

              const SizedBox(height: 32),

              // Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(
                          color: AppColors.gold.withOpacity(0.5),
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: Text(
                        'Cancel',
                        style: AppTypography.labelText.copyWith(
                          color: AppColors.gold,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _handleDownload,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.gold,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: Text(
                        'Download',
                        style: AppTypography.labelText.copyWith(
                          color: AppColors.darkPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOption({
    required int index,
    required String label,
    required String subtitle,
  }) {
    final isSelected = _selectedOption == index;
    return GestureDetector(
      onTap: () => setState(() => _selectedOption = index),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected
                ? AppColors.gold
                : AppColors.gold.withOpacity(0.2),
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(8),
          color: isSelected
              ? AppColors.gold.withOpacity(0.05)
              : Colors.transparent,
        ),
        child: Row(
          children: [
            Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: AppColors.gold,
                  width: 2,
                ),
              ),
              child: isSelected
                  ? Center(
                      child: Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: AppColors.gold,
                        ),
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: AppTypography.labelText.copyWith(
                      color: AppColors.cream,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: AppTypography.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                      fontSize: 12,
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
}
