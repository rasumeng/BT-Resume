# Development Log

## 2026-06-12 — Architecture Shift: Flutter Desktop → Web UI + CLI

### Decision: Replace Flutter Desktop with Web UI + CLI Tool

**Why?**

The original BTF Resume shipped as a Flutter Windows desktop application with
an embedded Python backend (`py_engine_desktop`). While functional, this
architecture had significant friction:

1. **Distribution complexity** — Required NSIS installer, Windows-specific
   builds, auto-update infrastructure, and a complex first-run setup that
   extracted Python assets from the Flutter binary.

2. **Cross-platform pain** — Flutter desktop requires separate builds for
   Windows, macOS, and Linux. Each has different quirks, bundling strategies,
   and update mechanisms.

3. **User experience gap** — Non-technical users found the installer flow
   confusing. The app required Ollama to be running, Python to be embedded,
   and a Flask server to be started—all invisible to the user but fragile.

4. **Maintenance burden** — Every change required rebuilding Flutter's Dart
   code, re-bundling Python assets, and re-running the NSIS build pipeline.
   Developer iteration was slow (~1-2 min per compile).

**The New Approach: Web UI + CLI Tool**

Modeled after successful local AI tools like OpenWebUI and Ollama's own
interface, the new architecture is:

```
btr (CLI command — typed in terminal)
 │
 ├── Auto-installs/starts Ollama
 ├── Starts Python Flask server
 └── Opens browser to http://localhost:5000
```

- **Frontend**: React SPA (TypeScript + Vite) served as static files from Flask
- **Backend**: Existing Python Flask API (unchanged, runs locally)
- **CLI**: Thin Python entry point (`btr` command)
- **Distribution**: `pip install btr-resume` or optional npm shim

**Key Benefits:**

| Concern | Before (Flutter) | After (Web + CLI) |
|---|---|---|
| Install | NSIS .exe installer | `pip install btr-resume` |
| First run | Extract Python, download Ollama | `btr setup` → auto everything |
| Cross-platform | 3 separate builds | Works everywhere (browser) |
| Dev iteration | ~90s Flutter compile | Instant HMR (Vite dev server) |
| UI updates | Dart rebuild + bundle | Hot reload + rebuild SPA |
| Distribution | GitHub Releases + auto-updater | PyPI / npm |
| Mobile/tablet | No | Yes (LAN access) |

**What Stays the Same:**

- All Python backend code (Flask routes, services, Ollama integration)
- The resume processing pipeline (polish, tailor, grade, parse)
- PDF generation (ReportLab)
- Ollama local LLM inference
- 100% offline, no API keys, no data leaving the machine

**What Changes:**

- Flutter app (`flutter_app/`) → Archived. No longer the primary UI.
- New `web/` directory → React SPA replicating the Flutter UI exactly.
- New `btr/` Python package → CLI entry point.
- `backend/app.py` → Minor update: serve web static files.
- `pyproject.toml` → New: define `btr` console script.

**Status:** Migration complete. Flutter code has now been removed.

## Implementation Details

### Project Structure (New/Modified Files)

```
resume-ai/
├── btr/                          # NEW: CLI Python package
│   ├── __init__.py
│   ├── __main__.py               # python -m btr
│   └── cli.py                    # btr, btr serve, btr setup commands
├── web/                          # NEW: React SPA frontend
│   ├── public/
│   │   ├── BTR-Logo.png          # Copied from flutter_app
│   │   └── favicon.svg           # Custom favicon
│   ├── src/
│   │   ├── api/client.ts         # API client (mirrors api_service.dart)
│   │   ├── components/           # 10 reusable components
│   │   │   ├── Card.tsx
│   │   │   ├── Button.tsx        # 5 variants
│   │   │   ├── TextField.tsx
│   │   │   ├── SegmentedControl.tsx  # pill + block styles
│   │   │   ├── CircularGauge.tsx     # SVG score gauge
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── Overlay.tsx
│   │   │   ├── NotificationDialog.tsx
│   │   │   └── BackendStatusBanner.tsx
│   │   ├── screens/              # 7 screens matching Flutter exactly
│   │   │   ├── SplashScreen.tsx
│   │   │   ├── SetupScreen.tsx
│   │   │   ├── HomeScreen.tsx    # Tab shell (4 tabs)
│   │   │   ├── MyResumesScreen.tsx  # Two-panel
│   │   │   ├── PolishScreen.tsx     # Two-panel
│   │   │   ├── TailorScreen.tsx     # Two-panel
│   │   │   └── FeedbackScreen.tsx
│   │   ├── styles/               # Design system CSS
│   │   │   ├── colors.css        # 13 CSS variables from Flutter
│   │   │   ├── typography.css    # 8 classes from Flutter
│   │   │   ├── spacing.css       # 4px base system
│   │   │   ├── components.css    # Shared component styles
│   │   │   └── globals.css       # Reset + utilities
│   │   ├── App.tsx               # State management + routing
│   │   └── main.tsx              # Entry point
│   ├── package.json
│   ├── vite.config.ts            # Proxy /api to Flask
│   └── tsconfig.json
├── backend/app.py                # MODIFIED: serves web/dist/ static files
├── pyproject.toml                # NEW: btr console_scripts entry point
└── DEVELOPMENT_LOG.md            # NEW: this file
```

### Design System: Flutter → CSS Mapping

The Flutter design tokens were ported exactly to CSS custom properties:

| Flutter (colors.dart) | CSS Variable |
|---|---|
| `AppColors.darkPrimary` | `--color-dark-primary` |
| `AppColors.darkSecondary` | `--color-dark-secondary` |
| `AppColors.gold` | `--color-gold` |
| `AppColors.cream` | `--color-cream` |
| `AppColors.errorRed` | `--color-error` |
| `goldGradient` | `--gradient-gold` |

| Flutter (typography.dart) | CSS Class |
|---|---|
| `AppTypography.headingPageTitle` | `.text-heading-page-title` |
| `AppTypography.headingSectionTitle` | `.text-heading-section-title` |
| `AppTypography.headingCardTitle` | `.text-heading-card-title` |
| `AppTypography.bodyLarge` | `.text-body-large` |
| `AppTypography.bodyNormal` | `.text-body-normal` |
| `AppTypography.labelText` | `.text-label` |
| `AppTypography.scoreDisplay` | `.text-score-display` |
| `AppTypography.monospace` | `.text-mono` |

### Client-Side API Layer

The `src/api/client.ts` mirrors the Flutter `ApiService` class with the same endpoints:
- `/list-resumes`, `/get-resume`, `/delete-resume`
- `/extract-pdf-text`, `/parse-resume`
- `/polish-bullets`, `/polish-resume`, `/get-polish-changes`
- `/tailor-resume`, `/analyze-fit`
- `/grade-resume`
- `/save-text-pdf`
- `/submit-feedback`
- `/health`

### How to Run

```bash
# Development - two terminals:
cd web && npm run dev       # Vite dev server (port 5173, proxies /api to Flask)
python run_backend.py       # Flask backend (port 5000)

# Production:
npm run build               # Build web/dist/
pip install -e .            # Install btr CLI
btr                         # Start server + open browser
```

### Next Steps
1. Test the full end-to-end flow with real resume operations
2. Set up CI to build + publish to PyPI on tags
3. Create npm shim package for `npx btr-resume`
4. Add error monitoring and analytics

---

## 2026-06-17 — Cleanup: Remove Flutter Artifacts

**What was removed:**
- `flutter_app/` — Entire Flutter desktop app (no longer the primary UI)
- `installer/` — NSIS installer scripts (Flutter-specific)
- `releases/` — Flutter update manifests and install scripts
- `scripts/release.ps1`, `scripts/setup-gh-pages.ps1` — Flutter release automation
- `.github/workflows/build.yml`, `.github/workflows/release.yml` — Flutter CI/CD
- `START_APP.bat`, `START_APP.ps1` — Old launcher scripts
- `debug_routes.py`, `test_upload_flow.py` — Debug utilities
- `samples/`, `resumes/` — Sample data directories
- Flutter fallback paths in `backend/services/file_service.py`
- Flutter entry in `.gitignore`

**Current focus:** Transform `btr-resume` into a pip-installable package with `btr serve` as the primary entry point, following the open-webui / opencode distribution pattern.
