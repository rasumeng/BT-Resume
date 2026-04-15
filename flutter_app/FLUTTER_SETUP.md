# Flutter Setup Guide

## Prerequisites

1. **Flutter SDK** - [Install Flutter](https://flutter.dev/docs/get-started/install)
   - Minimum version: 3.0.0
   - Windows support enabled

2. **Backend Running** - The Flask backend must be running:
   ```bash
   cd ..
   python run_backend.py
   ```

3. **Ollama** - Must be installed and running
   ```bash
   ollama serve
   ```

## Setup

### 1. Install Dependencies

```bash
flutter pub get
```

### 2. Generate Model Files

```bash
flutter pub run build_runner build
```

### 3. Run on Windows Desktop

```bash
flutter run -d windows
```

### 4. Build Release Executable

```bash
flutter build windows --release
```

Output: `./build/windows/x64/Release/btf_resume.exe`

## Architecture

```
Flutter Desktop App
   ↓ HTTP/JSON
Flask Backend (localhost:5000)
   ↓
Python Core Logic
   ↓ Ollama API
Ollama LLMs
```

## Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart              # App entry point
│   ├── constants/             # App constants & config
│   ├── models/                # Data models (with JSON serialization)
│   ├── services/              # API service (Flask communication)
│   ├── providers/             # State management (Provider)
│   ├── screens/               # UI screens
│   │   ├── splash_screen.dart    # Backend startup verification
│   │   └── home_screen.dart      # Main UI with tabs
│   └── widgets/               # Reusable widgets
├── windows/                   # Windows desktop build config
├── pubspec.yaml               # Dependencies
└── README.md                  # This file
```

## Key Components

### ApiService (`lib/services/api_service.dart`)
- Singleton pattern for Flask API communication
- Methods for all resume operations
- Built-in error handling and logging

### Models (`lib/models/resume_model.dart`)
- Dart equivalents of Python backend models
- JSON serialization support
- Type safety

### Screens
- **SplashScreen**: Waits for backend health check
- **HomeScreen**: Main tabs for resume operations

## Common Issues

### Backend not responding
- Check Flask backend is running: `python run_backend.py`
- Check Ollama is running: `ollama serve`
- Check port 5000 is not in use

### Models not generating
```bash
flutter pub run build_runner clean
flutter pub run build_runner build
```

### Build errors
```bash
flutter clean
flutter pub get
flutter pub run build_runner build
```

## Development

### Add new API endpoint
1. Create method in `ApiService` (lib/services/api_service.dart)
2. Create request/response models in `lib/models/resume_model.dart`
3. Add JSON serialization annotations
4. Update Resume routes in Python Flask backend

### Add new screen
1. Create file in `lib/screens/`
2. Create state management provider in `lib/providers/`
3. Add navigation in main.dart or from another screen

## Performance Tips

- Run in release mode for testing: `flutter run -d windows --release`
- LLM operations are slow (expected) - show loading indicators
- Cache resume lists to avoid repeated API calls

## Next Steps

1. [ ] Implement file picker for uploading resumes
2. [ ] Implement Polish feature UI and logic
3. [ ] Implement Tailor feature UI and logic
4. [ ] Implement Grade feature UI and logic
5. [ ] Add PDF preview
6. [ ] Create installer (MSIX) for distribution
