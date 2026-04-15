import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/resume_model.dart';
import 'polish_screen.dart';
import 'tailor_screen.dart';
import 'grade_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late ApiService _apiService;
  List<ResumeFile> resumes = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _apiService = ApiService();
    _loadResumes();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadResumes() async {
    try {
      final data = await _apiService.listResumes();
      setState(() {
        resumes = data;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading resumes: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('BTF Resume'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'My Resumes'),
            Tab(text: 'Polish'),
            Tab(text: 'Tailor'),
            Tab(text: 'Grade'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildMyResumesTab(),
          PolishScreen(resumes: resumes),
          TailorScreen(resumes: resumes),
          GradeScreen(resumes: resumes),
        ],
      ),
    );
  }

  Widget _buildMyResumesTab() {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (resumes.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              '📋 No resumes yet',
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 10),
            const Text('Upload a resume to get started'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Upload feature coming soon')),
              ),
              child: const Text('Upload Resume'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: resumes.length,
      itemBuilder: (context, index) {
        final resume = resumes[index];
        return Card(
          child: ListTile(
            leading: Icon(
              resume.isPdf ? Icons.picture_as_pdf : Icons.description,
              color: const Color(0xFFC9A84C),
            ),
            title: Text(resume.name),
            subtitle: Text('${(resume.size / 1024).toStringAsFixed(1)} KB'),
            trailing: PopupMenuButton(
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'delete',
                  child: Text('Delete'),
                ),
              ],
              onSelected: (value) {
                if (value == 'delete') {
                  _deleteResume(resume.name);
                }
              },
            ),
          ),
        );
      },
    );
  }

  Future<void> _deleteResume(String filename) async {
    try {
      await _apiService.deleteResume(filename);
      _loadResumes();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$filename deleted')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error deleting resume: $e')),
        );
      }
    }
  }
}
