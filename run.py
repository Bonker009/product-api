#!/usr/bin/env python3
"""
Startup script for the Product Management API.
This script provides an easy way to run the FastAPI application.
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Main function to start the FastAPI application."""
    
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check if .env file exists
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Copy env.example to .env and configure your settings.")
        print("   Using default configuration...")
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print("🚀 Starting Product Management API...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {reload}")
    print(f"   Log Level: {log_level}")
    print()
    print("📚 API Documentation will be available at:")
    print(f"   Swagger UI: http://{host}:{port}/api/v1/docs")
    print(f"   ReDoc: http://{host}:{port}/api/v1/redoc")
    print(f"   Health Check: http://{host}:{port}/health")
    print()
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 