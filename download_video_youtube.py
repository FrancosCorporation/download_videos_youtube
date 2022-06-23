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

    # "https://www.youtube.com/watch?v=FrQnTfxFZrA&list=PLtNhdKpTvTBMqFebVXMOytsjb-Qq0CV1A&index=17"
    youtube = YouTube(values[0])
    video = youtube.streams.get_highest_resolution().download()
    """def resize(input_file_path, output_file_path, width, height):
        comando_ffmpeg = "powershell ./ffmpeg/bin/ffmpeg.exe -i {input} -vf scale={width}:{height} {output}"
        print(comando_ffmpeg)
        os.system(f''+ comando_ffmpeg .format(
            input=input_file_path, width=width, height=height, output=output_file_path))
    resize(video, "resize_video.mp4", 720, 680 )"""
    window = sg.Window('Baixar Videos Youtube', [
                       [sg.Text('Concluido !!'), sg.Button('Ok')]])
    event, values = window.read()
