import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../config/colors.dart';
import '../../../config/typography.dart';
import '../../../core/services/resume_file_service.dart';
import '../../resumes/presentation/screens/my_resumes_screen.dart';

// ============================================================================
// Init Stages Enum
// ============================================================================
enum InitStage {
  checkingBackend,
  loadingLLM,
  ready,
  error,
}

// ============================================================================
// SplashScreen StatefulWidget
// ============================================================================
class SplashScreen extends StatefulWidget {
  final VoidCallback onReady;

  const SplashScreen({
    Key? key,
    required this.onReady,
  }) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

// ============================================================================
// _SplashScreenState
// ============================================================================
class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  String _statusMessage = 'Initializing...';
  bool _isError = false;
  bool _isRetrying = false;

  InitStage _currentStage = InitStage.checkingBackend;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();

    // Start initialization
    _initializeApp();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  // --------------------------------------------------------------------------
  // METHOD: Initialize App (Check Backend & LLM)
  // --------------------------------------------------------------------------
  Future<void> _initializeApp() async {
    try {
      // Step 0: Initialize resumes folder
      setState(() {
        _statusMessage = 'Preparing resumes folder...';
        _currentStage = InitStage.checkingBackend;
        _isError = false;
      });

      try {
        await ResumeFileService.ensureResumesFolderExists();
      } catch (e) {
        _showError('Failed to create resumes folder: ${e.toString()}');
        return;
      }

      setState(() {
        _statusMessage = 'Starting AI engine...';
        _currentStage = InitStage.checkingBackend;
      });

      // Step 1: Check backend health
      final backendReady = await _checkBackendHealth();
      if (!backendReady) {
        _showError(
          'Unable to start AI engine\n\n'
          'This usually means:\n'
          '• Ollama is not installed or running\n'
          '• Your computer needs more resources\n'
          '• A port is blocked\n\n'
          'Try: Close other apps and retry, or\n'
          'Install Ollama from https://ollama.ai',
        );
        return;
      }

      setState(() {
        _statusMessage = 'Loading your resume assistant...';
        _currentStage = InitStage.loadingLLM;
      });

      // Step 2: Wait for LLM to be ready
      final llmReady = await _waitForLLMReady();
      if (!llmReady) {
        _showError(
          'Resume assistant took too long to load\n\n'
          'This usually means:\n'
          '• Your computer is busy with other tasks\n'
          '• The AI model is very large (2.2GB)\n'
          '• Network connection issue\n\n'
          'Try: Close other apps, restart, and retry.',
        );
        return;
      }

      // Step 3: Success!
      setState(() {
        _statusMessage = 'Ready!';
        _currentStage = InitStage.ready;
      });

      // Small delay for visual feedback
      await Future.delayed(const Duration(milliseconds: 500));

      if (mounted) {
        widget.onReady();
      }
    } catch (e) {
      _showError('Initialization error: ${e.toString()}');
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Check Backend Health
  // --------------------------------------------------------------------------
  Future<bool> _checkBackendHealth() async {
    try {
      final dio = Dio();
      final response = await dio.get(
        'http://127.0.0.1:5000/api/health',
        options: Options(
          validateStatus: (status) => status != null && status < 500,
          sendTimeout: const Duration(seconds: 5),
          receiveTimeout: const Duration(seconds: 5),
        ),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('Backend health check error: $e');
      return false;
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Wait for LLM Ready (Poll /api/health)
  // --------------------------------------------------------------------------
  Future<bool> _waitForLLMReady() async {
    const maxAttempts = 60; // 60 attempts * 1 second = 60 seconds max
    int attempts = 0;

    while (attempts < maxAttempts) {
      try {
        final dio = Dio();
        final response = await dio.get(
          'http://127.0.0.1:5000/api/health',
          options: Options(
            validateStatus: (status) => status != null && status < 500,
            sendTimeout: const Duration(seconds: 5),
            receiveTimeout: const Duration(seconds: 5),
          ),
        );

        if (response.statusCode == 200) {
          final data = response.data as Map<String, dynamic>;
          final llmReady = data['llm_ready'] as bool? ?? false;

          if (llmReady) {
            return true; // LLM is ready!
          }
        }

        // Not ready yet, wait and retry
        await Future.delayed(const Duration(seconds: 1));
        attempts++;

        if (mounted) {
          // Show friendly progress message
          final progress = attempts < 10 ? 'Starting...' :
                          attempts < 20 ? 'Loading model...' :
                          attempts < 30 ? 'Almost ready...' :
                          'Still loading (this may take a minute)...';
          setState(() {
            _statusMessage = 'Loading your resume assistant...\n\n$progress';
          });
        }
      } catch (e) {
        print('LLM ready check error: $e');
        await Future.delayed(const Duration(seconds: 1));
        attempts++;
      }
    }

    return false; // Timeout
  }

  // --------------------------------------------------------------------------
  // METHOD: Show Error and Offer Retry
  // --------------------------------------------------------------------------
  void _showError(String message) {
    if (mounted) {
      setState(() {
        _statusMessage = message;
        _currentStage = InitStage.error;
        _isError = true;
      });
    }
  }

  // --------------------------------------------------------------------------
  // METHOD: Retry Initialization
  // --------------------------------------------------------------------------
  void _retryInitialization() {
    if (!_isRetrying) {
      setState(() {
        _isRetrying = true;
      });
      _initializeApp();
    }
  }

  // --------------------------------------------------------------------------
  // BUILD: Main Widget
  // --------------------------------------------------------------------------
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.darkPrimary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // ================================================================
            // Logo/App Name
            // ================================================================
            Padding(
              padding: const EdgeInsets.only(bottom: 32),
              child: Column(
                children: [
                  Text(
                    'Beyond The Resume',
                    style: AppTypography.headingPageTitle.copyWith(
                      fontSize: 32,
                      color: AppColors.cream,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'AI-Powered Resume Tools',
                    style: AppTypography.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),

            // ================================================================
            // Loading Animation or Error State
            // ================================================================
            if (!_isError)
              Padding(
                padding: const EdgeInsets.only(bottom: 32),
                child: SizedBox(
                  width: 60,
                  height: 60,
                  child: RotationTransition(
                    turns: _animationController,
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: AppColors.gold.withOpacity(0.3),
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(30),
                      ),
                      child: Center(
                        child: Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: AppColors.gold,
                              width: 3,
                            ),
                            borderRadius: BorderRadius.circular(25),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              )
            else
              Padding(
                padding: const EdgeInsets.only(bottom: 32),
                child: Icon(
                  Icons.error_outline,
                  size: 60,
                  color: AppColors.errorRed,
                ),
              ),

            // ================================================================
            // Status Messages
            // ================================================================
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Column(
                children: [
                  // Main status message
                  Text(
                    _statusMessage,
                    textAlign: TextAlign.center,
                    style: AppTypography.labelText.copyWith(
                      color: _isError
                          ? AppColors.errorRed
                          : AppColors.cream,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),

                  // Sub-messages based on stage (user-friendly, not technical)
                  if (!_isError) ...[
                    const SizedBox(height: 16),
                    if (_currentStage == InitStage.checkingBackend)
                      Text(
                        'Initializing...',
                        textAlign: TextAlign.center,
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    if (_currentStage == InitStage.loadingLLM)
                      Text(
                        'Setting up your AI assistant (this takes ~30 seconds on first launch)...',
                        textAlign: TextAlign.center,
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    if (_currentStage == InitStage.ready)
                      Text(
                        'Ready to boost your resume! 🚀',
                        textAlign: TextAlign.center,
                        style: AppTypography.bodySmall.copyWith(
                          color: AppColors.successGreen,
                          fontSize: 12,
                        ),
                      ),
                  ],
                ],
              ),
            ),

            // ================================================================
            // Retry Button (if error)
            // ================================================================
            if (_isError)
              Padding(
                padding: const EdgeInsets.only(top: 32),
                child: ElevatedButton.icon(
                  onPressed: _retryInitialization,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.gold,
                    foregroundColor: AppColors.darkPrimary,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                  ),
                ),
              ),

            // ================================================================
            // Footer Text
            // ================================================================
            Padding(
              padding: const EdgeInsets.only(top: 48),
              child: Text(
                'Starting up your AI resume assistant...',
                style: AppTypography.bodySmall.copyWith(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// SplashWrapper: Load frontend immediately, backend boots in background
// ============================================================================
class SplashWrapper extends StatefulWidget {
  const SplashWrapper({Key? key}) : super(key: key);

  @override
  State<SplashWrapper> createState() => _SplashWrapperState();
}

class _SplashWrapperState extends State<SplashWrapper> {
  @override
  void initState() {
    super.initState();
    // Start backend health check in background (non-blocking)
    _startBackgroundHealthCheck();
  }

  /// Check backend health continuously in the background
  Future<void> _startBackgroundHealthCheck() async {
    const maxAttempts = 120; // 2 minutes total
    int attempts = 0;

    while (attempts < maxAttempts) {
      try {
        final dio = Dio();
        final response = await dio.get(
          'http://127.0.0.1:5000/api/health',
          options: Options(
            validateStatus: (status) => status != null && status < 500,
            sendTimeout: const Duration(seconds: 5),
            receiveTimeout: const Duration(seconds: 5),
          ),
        );

        if (response.statusCode == 200) {
          final data = response.data as Map<String, dynamic>;
          final llmReady = data['llm_ready'] as bool? ?? false;

          if (llmReady) {
            // Backend is ready - no UI update needed, just stop polling
            return;
          }
        }

        // Not ready yet, wait and retry
        await Future.delayed(const Duration(seconds: 1));
        attempts++;
      } catch (e) {
        // Silently continue polling
        await Future.delayed(const Duration(seconds: 1));
        attempts++;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Load frontend immediately - backend boots in background
    return MyResumesScreen();
  }
}
