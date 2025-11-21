#!/usr/bin/env python3
"""
Test Procedure Management System - Startup Script
Convenience script to run the application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    # Create app
    app = create_app()

    # Run with debug mode in development
    print("\n" + "="*60)
    print("  Test Procedure Management System")
    print("="*60)
    print(f"  Running on: http://localhost:5000")
    print(f"  Press CTRL+C to quit")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
