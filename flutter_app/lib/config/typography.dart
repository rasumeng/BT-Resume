import 'package:flutter/material.dart';
import 'colors.dart';

class AppTypography {
  static const String _fontFamily = 'Poppins';

  // Page Title - 32px, bold, cream
  static const TextStyle headingPageTitle = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: AppColors.cream,
    letterSpacing: 0.5,
  );

  // Section Title - 16px, bold, gold, uppercase
  static const TextStyle headingSectionTitle = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: AppColors.gold,
    letterSpacing: 2,
  );

  // Card Title - 14px, bold, cream
  static const TextStyle headingCardTitle = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.bold,
    color: AppColors.cream,
    letterSpacing: 0.5,
  );

  // Body Large - 14px, cream
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: AppColors.cream,
    height: 1.6,
  );

  // Body Normal - 12px, text-secondary
  static const TextStyle bodyNormal = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.5,
  );

  // Body Small - 11px, text-tertiary
  static const TextStyle bodySmall = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.w400,
    color: AppColors.textTertiary,
  );

  // Label Text - 11px, bold, gold, uppercase
  static const TextStyle labelText = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.bold,
    color: AppColors.gold,
    letterSpacing: 1.5,
  );

  // Score Display - 24px, bold, gold
  static const TextStyle scoreDisplay = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: AppColors.gold,
  );

  // Monospace (for code/experience)
  static const TextStyle monospace = TextStyle(
    fontFamily: 'Courier New',
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AppColors.cream,
    height: 1.6,
  );
}
