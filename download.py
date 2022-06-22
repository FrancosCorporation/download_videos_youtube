import os
os.system(f'powershell "pip install -r requirements.txt"')
import subprocess
import sys
import PySimpleGUI as sg
from pytube import YouTube

#import ffmpeg

sg.theme('DarkAmber')
path = subprocess.getoutput(f'powershell "$env:PATH"')+";c:\\FFMPEG\\bin;"
path.replace('"', "")
# Create the Window
window = sg.Window('Baixar Videos Youtube', [[sg.Text('Insira a Url: '), sg.InputText()],
                                             [sg.Button('Ok'), sg.Button('Cancel')]])
event, values = window.read()
if event == sg.WIN_CLOSED or event == 'Cancel':
    sys.exit()  # if user closes window or clicks cancel
else:
    window.close()
    if(os.path.exists("1.mp4")):
        os.remove("1.mp4")
    if(os.path.exists("1.mp3")):
        os.remove("1.mp3")

    youtube = YouTube(
        "https://www.youtube.com/watch?v=FrQnTfxFZrA&list=PLtNhdKpTvTBMqFebVXMOytsjb-Qq0CV1A&index=17")
    # values[0])
    audio = youtube.streams.filter(only_audio=True)[0].download()
    os.rename(audio, "1.mp3")
    video = youtube.streams.filter(res="1080p").first().download()
    os.rename(video, "1.mp4")
    if(not os.path.exists("c:\\FFMPEG")):
        commandFixFFmpeg = "cp -r 'FFMPEG' 'c:\\' ;"
        os.system(f'powershell "{commandFixFFmpeg}"')
    
    command = f"setx path '{path}'"
    os.system(f'powershell "{command}"')
    # ffmpeg -i 1.mp4 -i 1.mp3 -c:v copy -c:a mp3 -map 0:v:0 -map 1:a:0 out.mp4
    command = "ffmpeg -i 1.mp4 -i 1.mp3 -c:v copy -c:a mp3 -map 0:v:0 -map 1:a:0 out.mp4"
    os.system(f'powershell "{command}"')
    os.rename("out.mp4", video)

    os.remove("1.mp4")
    os.remove("1.mp3")

    window = sg.Window('Finish', [[sg.Text('Terminamos ! ')],
                                  [sg.Button('Ok')]])
    event, values = window.read()