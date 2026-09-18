#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app

if __name__ == "__main__":
    print("🚀 Starting Farming Life Backend...")
    print("📡 Server running at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
