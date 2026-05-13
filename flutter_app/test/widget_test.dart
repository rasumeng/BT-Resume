import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:btf_resume/features/resumes/presentation/screens/my_resumes_screen.dart';

void main() {
  testWidgets('My Resumes screen renders grade controls', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: MyResumesScreen())),
    );
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('My Resumes'), findsOneWidget);
    expect(find.text('Resume Grade'), findsOneWidget);
    expect(find.text('Get Fresh Grade'), findsOneWidget);
    expect(find.text('Add Resume'), findsOneWidget);

    await tester.tap(find.text('Get Fresh Grade'));
    await tester.pump();
    expect(find.text('No resume selected'), findsOneWidget);
  });
}
