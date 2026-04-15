#!/usr/bin/env python3
# Windows build configuration helper for Flutter

import os
import subprocess
import sys

def main():
    """Main entry point for Windows build setup."""
    print("📦 BTF Resume - Flutter Windows Setup")
    print("=" * 50)
    
    # Check if Flutter is installed
    try:
        result = subprocess.run(['flutter', '--version'], capture_output=True, text=True)
        print(f"✓ Flutter: {result.stdout.strip().split(chr(10))[0]}")
    except FileNotFoundError:
        print("✗ Flutter not found. Please install Flutter from https://flutter.dev")
        sys.exit(1)
    
    # Get current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"📁 Project: {project_root}")
    print("=" * 50)
    
    # Build commands
    print("\n🔨 Building Flutter Windows app...")
    build_cmd = ['flutter', 'build', 'windows', '--release']
    
    result = subprocess.run(build_cmd, cwd=script_dir)
    
    if result.returncode == 0:
        print("\n✓ Build successful!")
        exe_path = os.path.join(
            script_dir, 
            'build', 'windows', 'x64', 'Release', 'btf_resume.exe'
        )
        print(f"📍 Executable: {exe_path}")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
