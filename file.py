import os
import subprocess

#path = os.symlink(f'powershell "$env:PATH"')
path = subprocess.getoutput(f'powershell "$env:PATH"')+";c:\\FFMPEG\\bin;"
path.replace('"', "")
print("helllou")
print(path)