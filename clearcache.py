import os
import shutil

exclude = [".venv", ".vscode", ".idea", ".git", "assets", "docs"]


CLEARED = []

def clearcache(toclear, filepath):
    print(f"Checking: {filepath}")
    for item in os.listdir(filepath):
        if item in exclude:
            continue
        if os.path.isdir(os.path.join(filepath, item)):
            if item == toclear:
                shutil.rmtree(os.path.join(filepath, item))
                CLEARED.append(os.path.join(filepath, item))
            else:
                clearcache(toclear, os.path.join(filepath, item))

clearcache("__pycache__", os.getcwd())

for file in CLEARED:
    print(f"Cleared from: {file}")


