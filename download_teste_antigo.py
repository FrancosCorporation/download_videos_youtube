from pytube import YouTube
import PySimpleGUI as sg
import sys
import subprocess
import os
os.system(f'powershell "pip install -r requirements.txt"')

#import ffmpeg

sg.theme('DarkAmber')
#path = subprocess.getoutput(f'powershell "$env:PATH"')+";c:\\FFMPEG\\bin;"
#path.replace('"', "")
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
    
    print(youtube.streams.filter(res="1080p"))
    video = youtube.streams.filter(res="1080p").first().download()
    os.rename(video, "1.mp4")
    print(video)
    if(not os.path.exists("\\FFMPEG")):
        commandFixFFmpeg = "cp -r 'FFMPEG';"
        os.system(f'powershell "{commandFixFFmpeg}"')

    command = f"setx path '{os.path}'"
    os.system(f'powershell "{command}"')
    # ffmpeg -i 1.mp4 -i 1.mp3 -c:v copy -c:a mp3 -map 0:v:0 -map 1:a:0 out.mp4
    command = "ffmpeg -i 1.mp4 -i 1.mp3 -c:v copy -c:a mp3 -map 0:v:0 -map 1:a:0 1.mp4"
    os.system(f'powershell "{command}"')

    os.rename(video, "out.mp4")

    os.remove("1.mp4")
    os.remove("1.mp3")

    window = sg.Window('Finish', [[sg.Text('Terminamos ! ')],
                                  [sg.Button('Ok')]])
    event, values = window.read()
