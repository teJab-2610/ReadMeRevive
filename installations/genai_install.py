# cell2.py
import subprocess

def install_genai():
    # Your code from cell 2 goes here
    subprocess.run(['pip', 'install', '-q', '-U', 'google-generativeai'])
    
    # Example code
    print("Installing google-generativeai...")
