# 🚀 Resume AI Application - Quick Start Guide

## One-Click Launch

The Resume AI application can now be started with a single click!

### **Option 1: Easiest - Double-Click to Run**
1. Navigate to the project root folder (`d:\Projects\resume-ai\`)
2. **Double-click `START_APP.bat`**
3. The application will start automatically:
   - Backend server starts on `http://127.0.0.1:5000`
   - Frontend Flutter app launches after backend is ready
   - Both run in the background

### **Option 2: PowerShell Launch** 
```powershell
cd d:\Projects\resume-ai
powershell -ExecutionPolicy Bypass -File .\START_APP.ps1
```

## What Happens When You Launch

1. ✅ Existing processes are cleaned up (if any)
2. ✅ Backend server starts and initializes Ollama connection
3. ✅ Launcher waits for backend health check (`/api/health`)
4. ✅ Frontend Flutter app launches once backend is ready
5. ✅ Both processes run together and are monitored

## Monitoring

The launcher displays:
- ✓ Process startup confirmations with PIDs
- ⏳ Backend readiness status
- 🔄 Real-time monitoring of both processes
- ⚠️ Notifications if either process stops

## Stopping the Application

- **Close the Flutter window** → Frontend stops, backend keeps running
- **Close the backend terminal** → Backend stops (may prompt to stop Flutter)
- **Stop both** → Application fully shuts down

## Backend API Endpoints

Once running, access the API at:
- Health check: `http://127.0.0.1:5000/api/health`
- Full API: `http://127.0.0.1:5000/api/`

## Requirements

- Python 3.9+ (with venv activated)
- Flutter with Windows support
- Ollama running locally on port 11434 with `mistral:7b` model
- Windows PowerShell 5.0+

## Troubleshooting

**Backend doesn't start:**
- Check that Python venv is installed: `python -m venv venv`
- Verify Ollama is running: `ollama serve`
- Check for port 5000 conflicts: `netstat -ano | findstr :5000`

**Frontend doesn't launch:**
- Ensure Flutter is installed: `flutter doctor`
- Run from the flutter_app directory if manual launch needed
- Check that backend is actually listening on port 5000

**Both processes start but app crashes:**
- Check backend logs in the terminal
- Verify Ollama has `mistral:7b` loaded: `ollama list`
- Re-run: `ollama pull mistral:7b`

---

**This launcher is one step away from being a complete packaged .exe!** 
The architecture is now production-ready for distribution.
