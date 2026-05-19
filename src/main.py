"""
main.py
Deployment entrypoint for Streamlit cloud/local execution.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

os.system("streamlit run app/dashboard.py")