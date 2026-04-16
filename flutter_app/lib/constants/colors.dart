import 'package:flutter/material.dart';

class AppColors {
  // Primary & Secondary Colors
  static const Color darkPrimary = Color(0xFF1a1a2e);
  static const Color darkSecondary = Color(0xFF16213e);
  static const Color dark2 = Color(0xFF2d2d4a);
  static const Color dark3 = Color(0xFF3a3a54);
  static const Color dark4 = Color(0xFF4a4a64);

  // Accent Colors
  static const Color gold = Color(0xFFc9a84c);
  static const Color goldHover = Color(0xFFd4b85f);
  static const Color cream = Color(0xFFf5f5f5);

  // Text Colors
  static const Color textSecondary = Color(0xFFb0b0c0);
  static const Color textTertiary = Color(0xFF808090);

  // Status Colors
  static const Color errorRed = Color(0xFFe74c3c);
  static const Color warningOrange = Color(0xFFf39c12);
  static const Color successGreen = Color(0xFF27ae60);

  // Gradients
  static const LinearGradient goldGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [gold, goldHover],
  );

  static const LinearGradient panelHeaderGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [dark2, dark3],
  );

  // Shadows
  static const List<BoxShadow> cardShadow = [
    BoxShadow(
      color: Color(0x26000000),
      blurRadius: 16,
      offset: Offset(0, 4),
    ),
  ];

  static const List<BoxShadow> buttonShadow = [
    BoxShadow(
      color: Color(0x40c9a84c),
      blurRadius: 12,
      offset: Offset(0, 4),
    ),
  ];
}
