# cell3.py
import subprocess

def install_joern():
    # Your code from cell 3 goes here
    subprocess.run(['curl', '-L', 'https://github.com/joernio/joern/releases/latest/download/joern-install.sh', '-o', 'joern-install.sh'])
    subprocess.run(['chmod', 'u+x', 'joern-install.sh'])
    subprocess.run(['./joern-install.sh', '--interactive'])
    
    # Example code
    print("Running joern-install.sh...")
