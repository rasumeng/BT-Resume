import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'constants/app_constants.dart';
import 'services/api_service.dart';
import 'screens/home_screen.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConstants.appTitle,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        // Modern color scheme matching the HTML design
        primaryColor: const Color(0xFFC9A84C), // Gold
        scaffoldBackgroundColor: const Color(0xFF14141F), // Dark background
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1E1E2E),
          foregroundColor: Color(0xFFC9A84C),
          elevation: 1,
        ),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFFF5F0E8),
          ),
          bodyMedium: TextStyle(
            fontSize: 14,
            color: Color(0xFFC4BFBD),
          ),
        ),
        useMaterial3: true,
      ),
      home: const SplashScreen(),
    );
  }
}

/// Global service provider
class ServiceProvider with ChangeNotifier {
  final ApiService apiService = ApiService();
  bool isBackendReady = false;
  String? errorMessage;

  /// Wait for backend to be ready
  Future<bool> waitForBackend() async {
    final startTime = DateTime.now();
    final timeout =
        Duration(milliseconds: AppConstants.backendStartupTimeout);

    while (DateTime.now().difference(startTime) < timeout) {
      try {
        if (await apiService.checkHealth()) {
          isBackendReady = true;
          notifyListeners();
          return true;
        }
      } catch (e) {
        // Continue trying
      }

      // Wait before retry
      await Future.delayed(
        Duration(
          milliseconds: AppConstants.healthCheckRetryInterval,
        ),
      );
    }

    errorMessage = 'Backend startup timeout. Make sure Ollama is running.';
    notifyListeners();
    return false;
  }
}
