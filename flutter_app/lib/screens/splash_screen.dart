import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../main.dart';
import 'home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  late ServiceProvider _serviceProvider;

  @override
  void initState() {
    super.initState();
    _serviceProvider = ServiceProvider();
    _checkBackend();
  }

  Future<void> _checkBackend() async {
    final success = await _serviceProvider.waitForBackend();

    if (mounted) {
      if (success) {
        // Backend is ready, go to home
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => const HomeScreen(),
          ),
        );
      } else {
        // Show error
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_serviceProvider.errorMessage ?? 'Unknown error'),
            duration: const Duration(seconds: 5),
          ),
        );
        // Try again after a delay
        await Future.delayed(const Duration(seconds: 2));
        _checkBackend();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo/Title
            const Text(
              'BTF Resume',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Color(0xFFC9A84C),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'AI Resume Helper',
              style: TextStyle(
                fontSize: 14,
                color: Color(0xFFC4BFBD),
              ),
            ),
            const SizedBox(height: 40),
            // Loading indicator
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFC9A84C)),
            ),
            const SizedBox(height: 20),
            const Text(
              'Starting backend...',
              style: TextStyle(
                color: Color(0xFFC4BFBD),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
