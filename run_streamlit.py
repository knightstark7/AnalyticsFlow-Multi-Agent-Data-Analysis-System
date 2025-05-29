#!/usr/bin/env python3
"""
Launcher script for DATAGEN Streamlit Application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application"""
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    streamlit_app_path = current_dir / "streamlit_app.py"
    
    # Check if streamlit_app.py exists
    if not streamlit_app_path.exists():
        print("❌ Error: streamlit_app.py not found!")
        print(f"Expected path: {streamlit_app_path}")
        return
    
    print("🚀 Starting DATAGEN Streamlit Application...")
    print(f"📁 Application path: {streamlit_app_path}")
    print("🌐 The app will open in your default browser")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app_path),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 