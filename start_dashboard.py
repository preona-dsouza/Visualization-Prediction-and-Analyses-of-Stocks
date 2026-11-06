import subprocess
import webbrowser
import time
import os

# ============================================================
# PROJECT: Stock Market Analysis and Prediction Dashboard
# AUTHOR: Preona Dsouza
# COPYRIGHT: © 2026 Preona Dsouza. All Rights Reserved.
#
# Original project implementation and design by the author.
# Unauthorised copying, modification or redistribution
# is prohibited except where permitted by applicable law.
# ============================================================

PROJECT = r"C:\Users\Preona Dsouza\Desktop\finalstocks"
PYTHON = os.path.join(PROJECT, ".venv", "Scripts", "python.exe")

# Start applications in the background
commands = [
    [PYTHON, "visualize.py"],
    [PYTHON, "-m", "streamlit", "run", "predict.py",
     "--server.port", "8501", "--server.headless", "true"],
    [PYTHON, "-m", "streamlit", "run", "Analysis.py",
     "--server.port", "8502", "--server.headless", "true"],
    [PYTHON, "-m", "streamlit", "run", "simulation_and_analysis.py",
     "--server.port", "8503", "--server.headless", "true"]
]

processes = []

for command in commands:
    process = subprocess.Popen(
        command,
        cwd=PROJECT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    processes.append(process)

# Start the HTML landing page server
server = subprocess.Popen(
    [PYTHON, "-m", "http.server", "8000"],
    cwd=PROJECT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)

processes.append(server)

# Wait for servers to start
time.sleep(5)

# Open the landing page
webbrowser.open("http://127.0.0.1:8000/navbarpage.html")

print("Dashboard started successfully.")
input("Press Enter to exit launcher...")