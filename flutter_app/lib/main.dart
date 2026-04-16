import 'package:flutter/material.dart';
import 'constants/colors.dart';
import 'constants/typography.dart';
import 'screens/my_resumes_screen.dart';
import 'screens/polish_screen.dart';
import 'screens/tailor_screen.dart';
import 'screens/feedback_screen.dart';

void main() {
  runApp(const BTFResumeApp());
}

class BTFResumeApp extends StatelessWidget {
  const BTFResumeApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Beyond The Resume',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        primaryColor: AppColors.darkPrimary,
        scaffoldBackgroundColor: AppColors.darkPrimary,
        colorScheme: ColorScheme.dark(
          primary: AppColors.gold,
          secondary: AppColors.darkSecondary,
          surface: AppColors.dark2,
          error: AppColors.errorRed,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.darkPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.darkPrimary,
        elevation: 0,
        title: Row(
          children: [
            Image.asset(
              'assets/icons/BTR-Logo.png',
              width: 100,
              height: 100,
              fit: BoxFit.contain,
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Save Time, Start Applying',
                  style: AppTypography.headingPageTitle.copyWith(
                    fontSize: 20,
                    color: AppColors.cream,
                  ),
                ),
                Text(
                  'All-in-One Resume Builder Powered by AI',
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '📄 MY RESUMES'),
            Tab(text: '✨ POLISH'),
            Tab(text: '🎯 TAILOR'),
            Tab(text: '⚡ FEEDBACK'),
          ],
          labelColor: AppColors.gold,
          unselectedLabelColor: AppColors.textSecondary,
          dividerColor: AppColors.gold,
          indicator: UnderlineTabIndicator(
            borderSide: BorderSide(
              color: AppColors.gold,
              width: 4,
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // My Resumes Tab
          const MyResumesScreen(),
          // Polish Tab
          const PolishScreen(),
          // Tailor Tab
          const TailorScreen(),
          // Experience Tab
          const FeedbackScreen(),
        ],
      ),
    );
  }

  Widget _buildPlaceholderTab(String title) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            title,
            style: AppTypography.headingPageTitle.copyWith(
              color: AppColors.cream,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Ready to build',
            style: AppTypography.bodyLarge.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
