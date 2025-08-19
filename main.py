import os
import sys

# Force working directory to script folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("RUNNING: This is the NEW code!")


from gui import run_gui

if __name__ == "__main__":
    run_gui()
