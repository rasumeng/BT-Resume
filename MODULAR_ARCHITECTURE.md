## Resume AI - Modular Architecture Refactoring Guide

This document outlines the new modular structure of the Resume AI project after comprehensive refactoring.

---

## Backend Python Structure

### Core Module (`core/`)

#### Prompts Package (`core/prompts/`)
Organized prompt templates separated by functionality:

```
core/prompts/
├── __init__.py                    # Re-exports all prompts for convenience
├── bullet_prompts.py              # Single bullet polishing and generation
├── resume_prompts.py              # Full resume polishing and change summaries
├── job_prompts.py                 # Job tailoring prompts
├── grading_prompts.py             # Resume grading and evaluation
└── parsing_prompts.py             # Resume parsing and structure extraction
```

**Usage:**
```python
# Import specific prompts
from core.prompts import bullet_polish_prompt, resume_polish_prompt

# Or import from specific modules
from core.prompts.bullet_prompts import bullet_polish_prompt
from core.prompts.resume_prompts import resume_polish_prompt
```

#### PDF Module (`core/pdf/`)
Professional PDF generation with modular components:

```
core/pdf/
├── __init__.py                    # Exports generate_pdf for backward compatibility
├── generator.py                   # Main generate_pdf function
├── styling.py                     # ReportLab paragraph styles
└── components.py                  # Reusable UI components (hr, bullet, two_col_row, etc.)
```

**Usage:**
```python
from core.pdf import generate_pdf
generate_pdf(resume_data, output_path)
```

#### Other Core Modules
- `resume_model.py` - ResumData and related data classes
- `utils.py` - Utility functions

---

### Backend Services (`backend/services/`)

#### LLM Service Package (`backend/services/llm/`)
Modular LLM operations with separated concerns:

```
backend/services/llm/
├── __init__.py                    # Exports LLMService
├── service.py                     # Main LLMService class with all LLM operations
└── parsers.py                     # JSON extraction, parsing, and validation
```

**LLMService Methods:**
- `call_ollama(prompt, stream=False)` - Direct Ollama call
- `polish_bullets(bullets, intensity)` - Polish individual bullets
- `polish_resume(resume_text, intensity)` - Polish entire resume
- `grade_resume(resume_text)` - Grade and evaluate resume
- `get_changes_summary(original, polished)` - Summarize changes
- `parse_to_pdf_format(resume_text)` - Parse resume to structured format

**Parsers Functions:**
- `extract_json_from_response(response)` - Extract JSON from LLM response
- `validate_parsed_resume(parsed)` - Validate resume structure
- `extract_bullet_list(response)` - Extract bullet points
- `extract_grade_data(response)` - Extract grade information

**Usage:**
```python
from backend.services.llm import LLMService
from backend.services.llm.parsers import extract_json_from_response

result = LLMService.polish_resume(text, intensity="medium")
parsed = extract_json_from_response(llm_response)
```

#### Other Service Modules
- `file_service.py` - File operations and resume management
- `job_tailor_service.py` - Job tailoring operations
- `ollama_service.py` - Ollama LLM management
- `cache_service.py` - Caching operations
- `feedback_service.py` - Feedback handling
- `alteration_service.py` - Resume alterations

---

## Flutter App Structure

### Feature-Based Architecture
The Flutter app uses feature-driven architecture for better scalability:

```
lib/
├── main.dart                                # App entry point
├── config/                                  # App-wide configuration
│   ├── colors.dart
│   ├── typography.dart
│   └── app_constants.dart
├── core/                                    # Core business logic
│   ├── models/
│   │   ├── resume_model.dart
│   │   └── tailor_models.dart
│   └── services/
│       ├── api_service.dart
│       └── resume_file_service.dart
├── features/                                # Feature modules
│   ├── resumes/                            # Manage resumes feature
│   │   └── presentation/
│   │       ├── screens/
│   │       │   └── my_resumes_screen.dart
│   │       └── widgets/
│   ├── polish/                             # Polish resume feature
│   │   └── presentation/
│   │       └── screens/
│   │           └── polish_screen.dart
│   ├── tailor/                             # Job tailoring feature
│   │   └── presentation/
│   │       └── screens/
│   │           └── tailor_screen.dart
│   ├── feedback/                           # Resume feedback feature
│   │   └── presentation/
│   │       └── screens/
│   │           └── feedback_screen.dart
│   └── splash/                             # Splash screen
│       └── presentation/
│           └── splash_screen.dart
└── shared/                                  # Shared across features
    └── widgets/
        └── download_dialog.dart
```

### Key Improvements
1. **Separation of Concerns** - Each feature is isolated and self-contained
2. **Scalability** - Easy to add new features without affecting others
3. **Maintainability** - Clear structure makes code easier to navigate
4. **Reusability** - Shared widgets and services are centralized

---

## Import Changes

### Backend Python

**Old:**
```python
from backend.services.llm_service import LLMService
from core.pdf_generator import generate_pdf
from core.prompts import resume_polish_prompt
```

**New:**
```python
from backend.services.llm import LLMService
from core.pdf import generate_pdf
from core.prompts import resume_polish_prompt  # Still works via package
```

### Flutter

**Old:**
```dart
import '../constants/colors.dart';
import '../services/api_service.dart';
```

**New:**
```dart
import '../../config/colors.dart';
import '../../core/services/api_service.dart';
```

---

## Backward Compatibility

Old import paths are still supported through deprecation wrappers:
- `core.prompts.py` - Re-exports from `core.prompts/` package
- `backend/services/llm_service_deprecated.py` - Re-exports from `backend/services/llm/`
- `core/pdf_generator_deprecated.py` - Re-exports from `core/pdf/`

Warnings will be shown, but code using old imports will continue to work.

---

## Benefits of Modular Structure

### Maintainability
- Each module has a single responsibility
- Easier to locate and modify specific functionality
- Reduced cognitive load when working on features

### Scalability
- New features can be added without touching existing code
- Easy to add new LLM functions, PDF features, or app screens
- Prevents circular dependencies

### Testability
- Smaller, focused modules are easier to unit test
- Clear interfaces make mocking easier
- Isolated features can be tested independently

### Performance
- Better code splitting in Flutter builds
- Reduced memory footprint in Python
- Parallel development on different features

### Code Organization
- Related code is grouped together
- Clear separation between UI, logic, and data
- Consistent project structure across team

---

## Migration Checklist

If you're working with branches or integrating this:

- [ ] Backend imports updated to use `backend.services.llm`
- [ ] Backend imports updated to use `core.pdf`
- [ ] Backend imports updated to use `core.prompts`
- [ ] Flutter imports updated to use new feature paths
- [ ] Tests updated with new import paths
- [ ] Any documentation updated
- [ ] Run linting/formatting on all modified files
- [ ] Verify all features work with new structure

---

## File Reorganization Summary

### Moved Backend Files
- ✅ `core/prompts.py` → Split into `core/prompts/` package
- ✅ `core/pdf_generator.py` → Split into `core/pdf/` package
- ✅ `backend/services/llm_service.py` → Reorganized as `backend/services/llm/` package

### Moved Flutter Files
- ✅ `constants/*.dart` → `config/`
- ✅ `models/*.dart` → `core/models/`
- ✅ `services/*.dart` → `core/services/`
- ✅ `screens/*.dart` → `features/*/presentation/screens/`
- ✅ `widgets/*.dart` → `shared/widgets/` (or feature-specific widgets)
