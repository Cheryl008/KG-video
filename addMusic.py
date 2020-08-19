import subprocess
import imageio
import os
from PIL import Image

def video_add_mp3(file_name, mp3_file):
    outfile_name = file_name.split('.')[0] + '-txt.avi'
    subprocess.call('ffmpeg -i ' + file_name
                    + ' -i ' + mp3_file + ' -strict -2 -f mp4 '
                    + "final.avi", shell=True)



video_add_mp3("output.avi", "Music.mp3")