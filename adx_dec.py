import tkinter as tk
from tkinter import filedialog
import subprocess
import glob
import os
import sys
import configparser

# Create the configuration file if it doesn't exist
if not os.path.exists('config.ini'):
    config = configparser.ConfigParser()
    config.add_section('Paths')
    config.set('Paths', 'input_folder', '')
    config.set('Paths', 'output_folder', '')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
else:
    config = configparser.ConfigParser()
    config.read('config.ini')

def choose_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_var.set(folder_selected)
    save_config()

def choose_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)
    save_config()

def save_config():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    config_path = os.path.join(application_path, 'config.ini')
    if not config.has_section('Paths'):
        config.add_section('Paths')
    config.set('Paths', 'input_folder', input_folder_var.get())
    config.set('Paths', 'output_folder', output_folder_var.get())
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def load_config():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    config_path = os.path.join(application_path, 'config.ini')
    if os.path.exists(config_path):
        config.read(config_path)
        if 'Paths' in config and config.has_option('Paths', 'input_folder'):
            input_folder_var.set(config['Paths']['input_folder'])
        if 'Paths' in config and config.has_option('Paths', 'output_folder'):
            output_folder_var.set(config['Paths']['output_folder'])

def encode():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    frequency = frequency_var.get()
    channels = '1' if channels_var.get() == 'mono' else '2'
    
    # List all supported audio files in the input directory
    audio_extensions = ['*.adx', '*.mp3', '*.wav', '*.flac', '*.aac', '*.ogg', '*.opus', '*.mp4', '*.mp2']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(input_folder, ext)))
    
    for audio_file in audio_files:
        # Construct the output file name
        base_name = os.path.basename(audio_file)
        name_without_ext, file_ext = os.path.splitext(base_name)
        output_file = os.path.join(output_folder, f"{name_without_ext}.wav")
        
        # Construct the ffmpeg command with the -y flag and hide banner
        local_ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
        ffmpeg_command = [local_ffmpeg_path, "-hide_banner", "-y", "-i", os.path.normpath(audio_file), "-c:a", "pcm_s16le", "-ar", frequency, "-ac", channels, os.path.normpath(output_file)]
        
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Completed processing {os.path.basename(audio_file)}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {os.path.basename(audio_file)}: {e}")

# Create the main window
root = tk.Tk()
root.title("Audio Converter")

# Variables to store user choices
input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
frequency_var = tk.StringVar(value="44100")
channels_var = tk.StringVar(value="stereo")

# Load the configuration file
load_config()

# Create the GUI components
tk.Label(root, text="Choose input folder:").pack()
tk.Button(root, text="Browse...", command=choose_input_folder).pack()
tk.Entry(root, textvariable=input_folder_var, width=50).pack()

tk.Label(root, text="Choose output folder:").pack()
tk.Button(root, text="Browse...", command=choose_output_folder).pack()
tk.Entry(root, textvariable=output_folder_var, width=50).pack()

tk.Label(root, text="Choose frequency:").pack()
tk.OptionMenu(root, frequency_var, "44100", "32000", "22050", "16000", "11025").pack()

tk.Label(root, text="Choose number of channels:").pack()
tk.OptionMenu(root, channels_var, "stereo", "mono").pack()

tk.Button(root, text="Convert", command=encode).pack()

# Run the main loop
root.mainloop()