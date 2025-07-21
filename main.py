#!/usr/bin/env python3
"""
Laundry Service Chatbot Main Application
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Also add the current directory to Python path for config imports
sys.path.insert(0, str(current_dir))

try:
    import gradio as gr
    from src.ui.chatbot import create_chatbot_interface
    from config.settings import settings
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install gradio pydantic python-dotenv requests")
    sys.exit(1)

def main():
    """Main application entry point"""
    try:
        # Create chatbot interface
        interface = create_chatbot_interface()
        
        # Launch the application
        print("🧺 Starting Laundry Service Chatbot...")
        print(f"📍 Server will be available at: http://localhost:{getattr(settings, 'PORT', 7860)}")
        print("💡 Type 'start' in the chat to begin!")
        
        # Get settings with defaults
        host = getattr(settings, 'HOST', '127.0.0.1')
        port = getattr(settings, 'PORT', 7860)
        share = getattr(settings, 'SHARE', False)
        debug = getattr(settings, 'DEBUG', False)
        
        interface.launch(
            server_name=host,
            server_port=port,
            share=share,
            debug=debug,
            show_error=True,
            favicon_path=None,
            ssl_verify=False,
            quiet=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()